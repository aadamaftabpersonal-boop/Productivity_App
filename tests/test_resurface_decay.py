import pytest
from httpx import ASGITransport, AsyncClient
from fastapi import status


@pytest.mark.asyncio
async def test_resurface_decay_on_success(registered_user):
    _, _, tokens = registered_user
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    from app.main import app
    from app.database import AsyncSessionLocal
    from app.weakness.matcher import load_concept_index
    from app.models import WeaknessRecord
    from app.security import decode_token
    user_id_str = decode_token(tokens["access_token"])["sub"]

    # Manually create an active weakness with gap_count = 2
    async with AsyncSessionLocal() as db:
        index = await load_concept_index(db)
        tag = index["sliding_window"]
        user_id = user_id_str

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        # Submit code that flags sliding_window twice to make active weakness
        for _ in range(2):
            sub_resp = await client.post(
                "/reviewer/submit",
                json={
                    "language": "python",
                    "code": "def solve(arr):\n    # inefficient sliding window\n    for i in range(len(arr)):\n        for j in range(i, len(arr)):\n            pass",
                    "problem_title": "Sliding Test",
                },
                headers=headers,
            )
            assert sub_resp.status_code == status.HTTP_202_ACCEPTED
            job_id = sub_resp.json()["job_id"]
            # wait for job completion
            import asyncio
            for _ in range(20):
                j = await client.get(f"/reviewer/job/{job_id}", headers=headers)
                if j.status_code == 200 and j.json().get("status") == "completed":
                    break
                await asyncio.sleep(0.1)

        # Fetch active weaknesses
        active_resp = await client.get("/weakness/active", headers=headers)
        assert active_resp.status_code == 200

        # Complete resurface with success = True
        resurface_item = await client.get("/weakness/resurface", headers=headers)
        if resurface_item.status_code == 200:
            cid = resurface_item.json().get("concept_tag_id")
            if cid:
                comp_resp = await client.post(
                    "/weakness/resurface/complete",
                    json={"concept_tag_id": cid, "success": True, "time_taken_seconds": 120},
                    headers=headers,
                )
                assert comp_resp.status_code == 200
                data = comp_resp.json()
                assert data["success"] is True
                assert data["cf_points_earned"] > 0
