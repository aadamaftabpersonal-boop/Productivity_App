from app.reviewer.hints import get_gated_hint


def test_tier_1_no_data_leakage():
    """Asserts Tier 1 response contains only pattern hint and never leaks solutions or code diffs."""
    heuristics = {}
    retrieved = [{"display_name": "Sliding Window", "common_mistakes": ["O(N^2) reslicing"]}]
    review_data = {
        "time_complexity": "O(N)",
        "space_complexity": "O(1)",
        "suggestions": [{"issue": "Reslicing", "fix": "Use left pointer"}],
        "better_approach": "Use dynamic window boundaries",
        "code_diff": "--- original\n+++ optimal"
    }

    tier1 = get_gated_hint(heuristics, retrieved, review_data, unlocked_tier=1)
    assert tier1["tier"] == 1
    assert "Sliding Window" in tier1["pattern_hint"]
    assert "suggestions" not in tier1
    assert "better_approach" not in tier1
    assert "code_diff" not in tier1


def test_tier_2_adds_complexity_target_no_code():
    heuristics = {}
    retrieved = [{"display_name": "Two Pointers", "common_mistakes": []}]
    review_data = {
        "time_complexity": "O(N)",
        "space_complexity": "O(1)",
        "suggestions": [{"issue": "Nested loop", "fix": "Use two pointers"}],
        "better_approach": "Sort array and use two pointers",
        "code_diff": "--- original\n+++ optimal"
    }

    tier2 = get_gated_hint(heuristics, retrieved, review_data, unlocked_tier=2)
    assert tier2["tier"] == 2
    assert "O(N)" in tier2["constraint_hint"]
    assert "suggestions" not in tier2
    assert "better_approach" not in tier2


def test_tier_4_full_solution_unlocked():
    heuristics = {}
    retrieved = [{"display_name": "Two Pointers", "common_mistakes": []}]
    review_data = {
        "time_complexity": "O(N)",
        "space_complexity": "O(1)",
        "suggestions": [{"issue": "Nested loop", "fix": "Use two pointers"}],
        "better_approach": "Sort array and use two pointers",
        "code_diff": "--- original\n+++ optimal"
    }

    tier4 = get_gated_hint(heuristics, retrieved, review_data, unlocked_tier=4)
    assert tier4["tier"] == 4
    assert len(tier4["suggestions"]) == 1
    assert tier4["better_approach"] == "Sort array and use two pointers"
    assert tier4["code_diff"] == "--- original\n+++ optimal"
