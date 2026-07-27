import pytest
import httpx
from fastapi import status


@pytest.mark.asyncio
async def test_leaderboard_endpoint(registered_user):
    _, _, tokens = registered_user
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    from app.main import app
    from httpx import ASGITransport

    async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/leaderboard", headers=headers)
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert "mastery_score" in data[0]
        assert "badges" in data[0]
