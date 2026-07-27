import httpx
from typing import Dict, List, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert

from app.models import ConceptTag, WeaknessRecord
from app.weakness.matcher import load_concept_index, match_text_to_concept

CODEFORCES_API_URL = "https://codeforces.com/api/user.status"


async def fetch_codeforces_submissions(handle: str, count: int = 50) -> List[Dict[str, Any]]:
    """Fetch user submission history from public Codeforces API."""
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(CODEFORCES_API_URL, params={"handle": handle, "from": 1, "count": count})
        if resp.status_code != 200:
            raise ValueError(f"Codeforces API returned status {resp.status_code} for handle '{handle}'")

        data = resp.json()
        if data.get("status") != "OK":
            raise ValueError(data.get("comment", "Failed to fetch Codeforces status"))

        return data.get("result", [])


async def import_codeforces_history(db: AsyncSession, user_id, handle: str, count: int = 50) -> Dict[str, Any]:
    """Imports Codeforces submission history and backfills user's weakness records."""
    submissions = await fetch_codeforces_submissions(handle, count)
    concept_index = await load_concept_index(db)

    flagged_concepts: Dict[str, int] = {}
    total_parsed = 0

    for sub in submissions:
        total_parsed += 1
        verdict = sub.get("verdict")
        problem = sub.get("problem", {})
        tags = problem.get("tags", [])

        # If verdict is WRONG_ANSWER / TIME_LIMIT_EXCEEDED / MEMORY_LIMIT_EXCEEDED, count tags as weakness gaps
        if verdict in ("WRONG_ANSWER", "TIME_LIMIT_EXCEEDED", "MEMORY_LIMIT_EXCEEDED", "RUNTIME_ERROR"):
            for tag_name in tags:
                matched_tag = match_text_to_concept(tag_name, concept_index)
                if matched_tag:
                    flagged_concepts[matched_tag.canonical_name] = (
                        flagged_concepts.get(matched_tag.canonical_name, 0) + 1
                    )

    # Backfill WeaknessRecords in DB
    updated_records = []
    for canonical_name, gap_count in flagged_concepts.items():
        tag = concept_index.get(canonical_name)
        if not tag:
            continue

        stmt = pg_insert(WeaknessRecord).values(
            user_id=user_id,
            concept_tag_id=tag.id,
            gap_count=gap_count,
            is_active_weakness=(gap_count >= 2),
        )
        stmt = stmt.on_conflict_do_update(
            constraint="uq_user_concept",
            set_={
                "gap_count": WeaknessRecord.gap_count + gap_count,
                "is_active_weakness": (WeaknessRecord.gap_count + gap_count) >= 2,
            },
        )
        await db.execute(stmt)
        updated_records.append(canonical_name)

    await db.commit()

    return {
        "handle": handle,
        "submissions_imported": total_parsed,
        "weaknesses_backfilled": len(updated_records),
        "flagged_concepts": flagged_concepts,
    }
