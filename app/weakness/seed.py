import asyncio
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.models import ConceptTag
from app.weakness.taxonomy import CONCEPT_SEED_DATA

async def seed_concepts():
    async with AsyncSessionLocal() as db:
        for entry in CONCEPT_SEED_DATA:
            result = await db.execute(select(ConceptTag).where(ConceptTag.canonical_name == entry["canonical_name"]))
            if result.scalar_one_or_none():
                continue
            db.add(ConceptTag(**entry))
        await db.commit()

if __name__ == "__main__":
    asyncio.run(seed_concepts())