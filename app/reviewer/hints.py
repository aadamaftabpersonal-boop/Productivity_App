"""Progressive Hint Engine module.

Gates diagnostic hints in 3 progressive tiers to prevent early solution leakage:
Tier 1: Pattern Name Only ("This looks like a Sliding Window problem")
Tier 2: Target Complexity ("Optimal target is O(N) time, O(1) space")
Tier 3: Corner-Case Warnings (Common edge cases from RAG knowledge base)
Tier 4: Full Solution Review Unlock
"""
from typing import Dict, Any, List


def build_hint_tiers(heuristics: Dict[str, Any], retrieved: List[Dict[str, Any]], review_data: Dict[str, Any]) -> Dict[str, Any]:
    """Assembles progressive hint tiers from static facts, RAG retrieval, and review data."""
    primary_concept = "Algorithms & Data Structures"
    common_mistakes = ["Off-by-one boundary checks", "Empty array edge cases"]

    if retrieved:
        ref = retrieved[0]
        primary_concept = ref.get("display_name", primary_concept)
        common_mistakes = ref.get("common_mistakes", common_mistakes)

    tier1 = {
        "tier": 1,
        "tier_name": "Pattern Hint",
        "pattern_hint": f"This problem pattern relates to **{primary_concept}**.",
    }

    tier2 = {
        **tier1,
        "tier": 2,
        "tier_name": "Constraint & Complexity Target",
        "constraint_hint": f"Target complexity bound: **{review_data.get('time_complexity', 'O(N)')}** time, **{review_data.get('space_complexity', 'O(N)')}** space.",
    }

    tier3 = {
        **tier2,
        "tier": 3,
        "tier_name": "Corner-Case Warnings",
        "corner_case_hint": f"Watch out for common pitfalls: {', '.join(common_mistakes)}",
    }

    tier4 = {
        **tier3,
        "tier": 4,
        "tier_name": "Full Solution Review",
        "suggestions": review_data.get("suggestions", []),
        "better_approach": review_data.get("better_approach"),
        "code_diff": review_data.get("code_diff"),
    }

    return {
        1: tier1,
        2: tier2,
        3: tier3,
        4: tier4,
    }


def get_gated_hint(heuristics: Dict[str, Any], retrieved: List[Dict[str, Any]], review_data: Dict[str, Any], unlocked_tier: int = 1) -> Dict[str, Any]:
    """Returns strictly gated payload for the specified unlocked tier with no higher-tier data leakage."""
    tiers = build_hint_tiers(heuristics, retrieved, review_data)
    clamped_tier = max(1, min(unlocked_tier, 4))
    return tiers[clamped_tier]
