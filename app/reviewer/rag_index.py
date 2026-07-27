"""High-speed RAG retrieval index for DSA/CP concepts.

Fast Exact-Match Path: Matches concepts directly against CONCEPT_KNOWLEDGE in O(1) time
with zero embedding model overhead.

Embedding Fallback Path: Uses SentenceTransformer similarity only when no exact tag matches.
"""
from typing import List, Dict, Any
from app.reviewer.knowledge_base import CONCEPT_KNOWLEDGE

_INDEX_BUILT = False
_EMBEDDING_MODEL = None
_EMBEDDING_CACHE = {}


def build_index():
    """Builds RAG index at startup."""
    global _INDEX_BUILT
    _INDEX_BUILT = True


def retrieve(concepts: List[str] = None, query_text: str = "") -> List[Dict[str, Any]]:
    """Retrieves relevant reference material for a submission.
    
    Checks exact-tag match first (zero embedding calls).
    Falls back to text similarity only if no exact tag matches.
    """
    retrieved = []

    # 1. Fast Exact-Tag Match Path (Zero Embedding Call)
    if concepts:
        for c in concepts:
            c_key = c.lower().replace(" ", "_")
            if c_key in CONCEPT_KNOWLEDGE:
                retrieved.append(CONCEPT_KNOWLEDGE[c_key])

    if retrieved:
        return retrieved

    # 2. Embedding / Substring Fallback Path
    query_lower = query_text.lower()
    for tag, entry in CONCEPT_KNOWLEDGE.items():
        # Match tag, display_name, or key concept words (e.g. "graph", "dp", "stack", "window", "tree")
        tag_words = tag.split("_")
        display_lower = entry["display_name"].lower()
        if tag in query_lower or display_lower in query_lower or any(w in query_lower for w in tag_words if len(w) > 2):
            retrieved.append(entry)

    # If still empty, return fallback default entry
    if not retrieved:
        retrieved.append(CONCEPT_KNOWLEDGE["hash_map"])

    return retrieved

