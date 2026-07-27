import pytest
import httpx
from fastapi import status


@pytest.mark.asyncio
async def test_weakness_analytics_endpoint(registered_user):
    _, _, tokens = registered_user
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    from app.main import app
    from httpx import ASGITransport

    async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get("/weakness/analytics", headers=headers)
        assert resp.status_code == status.HTTP_200_OK
        data = resp.json()
        assert "mastery_radar" in data
        assert len(data["mastery_radar"]) >= 15
        assert "domain_stats" in data
        assert "cp" in data["domain_stats"]
