import pytest
from app.reviewer.rag_index import retrieve
from app.reviewer.diff_generator import generate_optimal_code_diff


def test_exact_tag_match_retrieval():
    """Asserts exact-tag match returns in-corpus content directly without error."""
    res = retrieve(concepts=["sliding_window"], query_text="")
    assert len(res) >= 1
    assert res[0]["tag"] == "sliding_window"
    assert "Sliding Window" in res[0]["display_name"]
    assert "canonical_solution" in res[0]


def test_embedding_fallback_retrieval():
    """Asserts text search fallback returns relevant concept for unseen query."""
    res = retrieve(concepts=[], query_text="Given a graph of connected components")
    assert len(res) >= 1
    assert "graph_traversal" in res[0]["tag"] or "graph" in res[0]["display_name"].lower()


@pytest.mark.asyncio
async def test_diff_generator_does_not_return_two_sum_for_non_two_sum():
    """Asserts diff generator uses canonical solution or generic patch, never hardcoded two sum."""
    code = """def solve_graph(adj):
    for u in adj:
        for v in adj[u]:
            print(u, v)
"""
    canonical_dp = """def solve_graph(adj):
    visited = set()
    for u in adj:
        if u not in visited:
            visited.add(u)
"""
    diff_patch = await generate_optimal_code_diff(code, language="python", canonical_solution=canonical_dp)
    assert "seen = {}" not in diff_patch
    assert "target - num" not in diff_patch
    assert "solve_graph" in diff_patch or "original.py" in diff_patch
