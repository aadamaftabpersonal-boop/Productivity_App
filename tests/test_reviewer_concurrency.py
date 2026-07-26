"""
This test exists specifically to catch a bug that shipped in an earlier version:
`get_review()` called the *synchronous* Groq SDK client directly inside an
`async def` FastAPI route. That blocks the entire event loop for the full
duration of the LLM call -- while one person's review was being generated,
the server could not serve ANY other request (login, health check, anything).

The fix was switching to Groq's AsyncGroq client and awaiting it properly.

DESIGN NOTE, because getting this test right took three attempts:

Attempt 1 (in-process ASGITransport, compare which of two concurrent requests
finishes first): passed against the FIXED code, but also passed against the
deliberately-reverted BUGGY code, i.e. it proved nothing. The in-process
transport has several genuine await points before the route handler body
even runs, which let a concurrent "fast" request race ahead regardless of
whether the handler itself blocks.

Attempt 2 (real live uvicorn server over a real socket, same
finish-order comparison): still passed against the buggy code, for a
different reason -- the route handler has legitimate `await` points (the DB
write) *before* it reaches the actual blocking call, so the fast request can
sneak through during that earlier window even when the real bug is present
later in the same handler.

Attempt 3 (this version): uses an explicit cross-thread signal that fires
the instant execution enters the mocked review call, right before it
starts blocking/sleeping. The test waits for that signal, THEN launches the
fast request -- guaranteeing it overlaps the exact window that matters,
instead of hoping ordering/timing happens to expose the bug.
"""
import asyncio
import socket
import threading
import time
import contextlib

import httpx
import pytest
import uvicorn

import app.routers.reviewer as reviewer_router
from app.main import app

pytestmark = pytest.mark.asyncio

SIMULATED_LLM_LATENCY_SECONDS = 1.2
FAST_REQUEST_MAX_ALLOWED_SECONDS = 0.4  # must stay well under the simulated latency


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@contextlib.contextmanager
def live_server():
    """Runs the real FastAPI app on a real port in a background thread."""
    port = _free_port()
    config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="error")
    server = uvicorn.Server(config)

    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()

    for _ in range(100):
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.1):
                break
        except OSError:
            time.sleep(0.05)
    else:
        raise RuntimeError("live test server never came up")

    try:
        yield f"http://127.0.0.1:{port}"
    finally:
        server.should_exit = True
        thread.join(timeout=5)


async def test_event_loop_not_blocked_during_review(registered_user, monkeypatch):
    entered_review_call = threading.Event()

    async def _fake_slow_get_review(*args, **kwargs):
        entered_review_call.set()
        await asyncio.sleep(SIMULATED_LLM_LATENCY_SECONDS)
        return {
            "time_complexity": "O(n)", "space_complexity": "O(1)",
            "concepts": [], "suggestions": [], "better_approach": "x", "score": 90,
        }

    monkeypatch.setattr(reviewer_router, "get_review", _fake_slow_get_review)

    _, _, tokens = registered_user
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    with live_server() as base_url:
        async with httpx.AsyncClient(base_url=base_url, timeout=10) as http:

            async def do_slow_review():
                return await http.post(
                    "/reviewer/submit",
                    json={
                        "language": "python",
                        "code": "def f(n):\n    return n * 2",
                        "problem_title": "Doubler",
                        "problem_statement": None,
                    },
                    headers=headers,
                )

            review_task = asyncio.create_task(do_slow_review())

            # Wait until execution has genuinely entered the mocked review
            # call -- i.e. we're now INSIDE the window that used to be a
            # blocking call -- before launching the "fast" request. This is
            # the piece that makes the test actually discriminate correctly.
            for _ in range(200):
                if entered_review_call.is_set():
                    break
                await asyncio.sleep(0.01)
            else:
                pytest.fail(
                    "The mocked review call was never entered within 2s. If "
                    "get_review() is being called without `await` again "
                    "(the original bug), the coroutine is created but never "
                    "actually runs, so this branch fires instead of a clean "
                    "timing failure -- that itself is the regression."
                )

            start = time.monotonic()
            fast_resp = await http.get("/health")
            fast_elapsed = time.monotonic() - start

            review_resp = await review_task

    assert fast_resp.status_code == 200
    assert review_resp.status_code == 201

    # THIS is the assertion that fails against the old synchronous-client
    # code: /health, requested WHILE the review call is actively in its
    # blocking/sleeping window, must still return almost immediately. If the
    # event loop is blocked, fast_elapsed balloons up toward
    # SIMULATED_LLM_LATENCY_SECONDS instead.
    assert fast_elapsed < FAST_REQUEST_MAX_ALLOWED_SECONDS, (
        f"/health took {fast_elapsed:.2f}s while a review call was actively "
        f"in flight -- the event loop appears to be blocked by the reviewer "
        f"call again."
    )

