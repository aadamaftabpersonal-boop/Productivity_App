import asyncio
import pytest
import httpx
from fastapi import status


@pytest.mark.asyncio
async def test_job_submission_and_status_polling(registered_user):
    _, _, tokens = registered_user
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    from app.main import app
    from httpx import ASGITransport

    async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Submit review
        submit_resp = await client.post(
            "/reviewer/submit",
            json={
                "language": "python",
                "code": "def solve(n):\n    return n * 2",
                "problem_title": "Doubler Job Test",
            },
            headers=headers,
        )

        assert submit_resp.status_code == status.HTTP_202_ACCEPTED
        body = submit_resp.json()
        assert body["status"] == "processing"
        job_id = body["job_id"]

        # Poll for completion (up to 3s)
        completed = False
        for _ in range(30):
            job_resp = await client.get(f"/reviewer/job/{job_id}", headers=headers)
            assert job_resp.status_code == 200
            data = job_resp.json()
            if data["status"] == "completed":
                completed = True
                assert data["submission"]["review"] is not None
                break
            await asyncio.sleep(0.1)

        assert completed is True
