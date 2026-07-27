import pytest
import asyncio
from httpx import ASGITransport, AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_calibration_stats_and_submit_predictions(registered_user):
    _, _, tokens = registered_user
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Submit code with calibration predictions
        sub_resp = await client.post(
            "/reviewer/submit",
            json={
                "language": "python",
                "code": "def solve(n):\n    return n * n",
                "user_predicted_complexity": "O(1)",
                "confidence_level": "high",
            },
            headers=headers,
        )
        assert sub_resp.status_code == 202
        job_id = sub_resp.json()["job_id"]

        # Poll for job completion
        for _ in range(20):
            j = await client.get(f"/reviewer/job/{job_id}", headers=headers)
            if j.status_code == 200 and j.json().get("status") == "completed":
                break
            await asyncio.sleep(0.1)

        # Fetch calibration stats
        stats_resp = await client.get("/reviewer/calibration-stats", headers=headers)
        assert stats_resp.status_code == 200
        data = stats_resp.json()
        assert "total_calibrated" in data
        assert data["total_calibrated"] >= 1
        assert "accuracy_percent" in data
