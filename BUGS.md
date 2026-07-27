# Known Issues

Tracked honestly, including ones already fixed, so the history of what was
wrong and when it got fixed stays visible rather than quietly disappearing.

## Fixed

### BUG-001: Event loop blocked during LLM review call
**Status: Fixed** (see commit that introduces `AsyncGroq`)

`get_review()` in `app/reviewer/llm_review.py` called the synchronous Groq
SDK client (`Groq`) directly inside an `async def` FastAPI route
(`app/routers/reviewer.py`). Since the call was never awaited (nothing to
await — it wasn't a coroutine), it ran synchronously on the request-handling
thread, blocking the single event loop for the full duration of the LLM
call. In practice: while one person's review was being generated, the
server could not serve *any* other request — no other user's login, no
health check, nothing — because FastAPI/uvicorn serve everything off that
one loop.

This directly contradicted the "async FastAPI backend" architecture claim on
its single most expensive, most frequently-hit code path.

**Fix**: switched to Groq's `AsyncGroq` client, made `get_review` an
`async def`, and awaited it properly at the call site.

**Regression test**: `tests/test_reviewer_concurrency.py`. Getting this test
to actually discriminate fixed-vs-buggy code took three attempts — see the
design note in that file. The short version: an in-process test client and
even a naive live-server test can both give false confidence, because there
are legitimate `await` points elsewhere in the handler that let a concurrent
request sneak through regardless of whether the specific line under test
blocks. The working version uses an explicit cross-thread signal fired the
instant execution enters the mocked call, so the "fast" concurrent request
is guaranteed to be launched during the exact window that matters.

### ISSUE-002: Real AST call-graph recursion & node type inspection
**Status: Fixed**

Replaced naive substring counting in `_detect_recursion` with scope-aware AST call-graph walking (extracting declared function names and matching `call` / `call_expression` / `method_invocation` callee identifiers). Replaced raw identifier keyword string matching in `_detect_data_structures` with AST type/declaration/constructor node inspection (`template_type` / `type_identifier` / `generic_type` / call nodes) across Python, C++, and Java. Decoy identifiers like `mapValue` or `solve_helper` no longer trigger false positive data structure hints or recursion flags.

**Regression test**: `tests/test_tree_analysis.py`.

## Open

### ISSUE-003: No independent verification of LLM complexity claims
Everything the review reports about time/space complexity is the LLM's own
output, fed structural facts as prompt context but never independently
checked against them. A wrong complexity claim currently ships with the
same confidence as a correct one.

### ISSUE-004: Resume claim of "Arq background jobs" doesn't match this repo
No `arq` dependency or usage exists in this codebase as of this commit.
Either implement it for real (queue the LLM review calls so they don't
compete with interactive request latency) or remove the claim wherever it's
stated externally.

### ISSUE-005: No rate limiting on auth endpoints
`/auth/login`, `/auth/register`, `/auth/refresh` have no rate limiting.

### ISSUE-006: No input size/sanitization limit on submitted code
Arbitrary user-submitted text is passed to the tree-sitter parser with no
size cap — worth stress-testing with adversarial/oversized input before
this is exposed to real users.
