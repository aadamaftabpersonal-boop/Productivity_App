import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_streak_discord_and_shareable_report(registered_user):
    _, _, tokens = registered_user
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # 1. Test Dashboard streak_days output
        dash_resp = await client.get("/dashboard", headers=headers)
        assert dash_resp.status_code == 200
        dash_data = dash_resp.json()
        assert "streak_days" in dash_data
        assert dash_data["streak_days"] >= 1

        # 2. Test Discord Webhook update
        discord_resp = await client.post(
            "/dashboard/discord-webhook",
            json={"webhook_url": "https://discord.com/api/webhooks/12345/test"},
            headers=headers,
        )
        assert discord_resp.status_code == 200
        assert "Discord Webhook saved" in discord_resp.json()["message"]

        # 3. Test Shareable Progress Report artifact
        report_resp = await client.get("/weakness/shareable-report", headers=headers)
        assert report_resp.status_code == 200
        report_data = report_resp.json()
        assert "linkedin_share_text" in report_data
        assert "resolved_weakness_count" in report_data
