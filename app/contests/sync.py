from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert as pg_insert
from app.models import Contest
from app.contests.fetchers import fetch_codeforces_contests, fetch_leetcode_contests


async def sync_contests(db: AsyncSession) -> dict:
    results = {"codeforces": 0, "leetcode": 0, "errors": []}

    fetchers = {
        "codeforces": fetch_codeforces_contests,
        "leetcode": fetch_leetcode_contests,
    }

    for platform, fetch_fn in fetchers.items():
        try:
            contests = await fetch_fn()
        except Exception as e:
            results["errors"].append(f"{platform}: {str(e)}")
            continue

        for c in contests:
            stmt = pg_insert(Contest).values(**c)
            stmt = stmt.on_conflict_do_update(
                constraint="uq_platform_external_id",
                set_={
                    "name": stmt.excluded.name,
                    "start_time": stmt.excluded.start_time,
                    "duration_seconds": stmt.excluded.duration_seconds,
                    "is_finished": stmt.excluded.is_finished,
                    "fetched_at": stmt.excluded.fetched_at,
                },
            )
            await db.execute(stmt)
        results[platform] = len(contests)

    await db.commit()
    return results