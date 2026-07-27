import pytest
import uuid
from datetime import datetime, timezone
from httpx import ASGITransport, AsyncClient
from app.main import app
from app.database import AsyncSessionLocal
from app.models import Contest


@pytest.mark.asyncio
async def test_generate_post_mortem(registered_user):
    _, _, tokens = registered_user
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    unique_ext_id = f"cf_test_pm_{uuid.uuid4().hex[:8]}"

    # Create dummy contest in db using datetime object and unique external_id
    async with AsyncSessionLocal() as db:
        c = Contest(
            platform="codeforces",
            external_id=unique_ext_id,
            name="Codeforces Round #999 (Div. 2)",
            start_time=datetime.now(timezone.utc),
            duration_seconds=7200,
            url=f"https://codeforces.com/contest/{unique_ext_id}",
            is_finished=True,
        )
        db.add(c)
        await db.commit()
        await db.refresh(c)
        contest_id = str(c.id)

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        resp = await client.get(f"/contests/{contest_id}/post-mortem", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "rank_impact_narrative" in data
        assert "concept_gaps" in data
