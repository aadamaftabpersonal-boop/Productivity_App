import pytest
from app.contests.leetcode_sync import import_leetcode_user_submissions


@pytest.mark.asyncio
async def test_leetcode_import_backfills_weaknesses(registered_user):
    _, _, tokens = registered_user
    from app.database import AsyncSessionLocal
    from app.security import decode_token
    user_id_str = decode_token(tokens["access_token"])["sub"]
    import uuid

    async with AsyncSessionLocal() as db:
        res = await import_leetcode_user_submissions("tourist", count=10, db=db, user_id=uuid.UUID(user_id_str))
        assert res["submissions_imported"] > 0
        assert "weaknesses_backfilled" in res
