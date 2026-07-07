from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import ConceptTag

async def load_concept_index(db: AsyncSession) -> dict[str, ConceptTag]:
    """alias/canonical_name (lowercased) -> ConceptTag, built once per call."""
    result = await db.execute(select(ConceptTag))
    tags = result.scalars().all()

    index = {}
    for tag in tags:
        index[tag.canonical_name.lower()] = tag
        index[tag.display_name.lower()] = tag
        for alias in tag.aliases:
            index[alias.lower()] = tag
    return index


def match_text_to_concept(text: str, index: dict[str, ConceptTag]) -> ConceptTag | None:
    """Substring match against the alias index. Not perfect NLP matching,
    but reliable enough given the LLM's phrasing is fairly consistent, and it's fully explainable
    (no black-box embedding similarity) which matters if you need to defend this design."""
    text_lower = text.lower()
    for alias, tag in index.items():
        if alias in text_lower:
            return tag
    return None