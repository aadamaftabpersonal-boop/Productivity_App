import pytest
import httpx
from fastapi import status


@pytest.mark.asyncio
async def test_oversized_code_submission_rejected(registered_user):
    _, _, tokens = registered_user
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    # Oversized payload exceeding 64KB
    huge_code = "x = 1\n" * 15000  # >90KB

    from app.main import app
    from httpx import ASGITransport

    async with httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.post(
            "/reviewer/submit",
            json={
                "language": "python",
                "code": huge_code,
                "problem_title": "Oversized Test",
            },
            headers=headers,
        )

    assert resp.status_code == status.HTTP_400_BAD_REQUEST
    assert "exceeds maximum limit" in resp.json()["detail"]
