import pytest
import httpx
from fastapi import status


@pytest.mark.asyncio
async def test_codeforces_import_backfills_weaknesses(registered_user, monkeypatch):
    _, _, tokens = registered_user
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    # Mock Codeforces user.status API response
    fake_cf_data = {
        "status": "OK",
        "result": [
            {
                "id": 101,
                "verdict": "TIME_LIMIT_EXCEEDED",
                "problem": {"name": "Sliding Window Max", "tags": ["two pointers", "sliding window"]},
            },
            {
                "id": 102,
                "verdict": "WRONG_ANSWER",
                "problem": {"name": "Sliding Window Sum", "tags": ["sliding window"]},
            },
            {
                "id": 103,
                "verdict": "OK",
                "problem": {"name": "Easy Sum", "tags": ["implementation"]},
            },
        ],
    }

    async def _fake_get(*args, **kwargs):
        class FakeResponse:
            status_code = 200
            def json(self):
                return fake_cf_data
        return FakeResponse()

    monkeypatch.setattr(httpx.AsyncClient, "get", _fake_get)

    from app.main import app
    from httpx import ASGITransport

    async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post(
            "/contests/import/codeforces",
            json={"handle": "tourist", "count": 10},
            headers=headers,
        )

    assert resp.status_code == status.HTTP_200_OK
    data = resp.json()
    assert data["handle"] == "tourist"
    assert data["submissions_imported"] == 3
    assert "sliding_window" in data["flagged_concepts"] or "sliding window" in str(data["flagged_concepts"]).lower()
