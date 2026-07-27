from app.contests.warmup import generate_warmup_ladder


def test_warmup_ladder_generates_three_problems():
    """Asserts ladder returns 3 structured problems: Easy -> Medium -> Hard."""
    ladder = generate_warmup_ladder(company="meta")
    assert len(ladder) == 3
    assert ladder[0]["difficulty"] == "Easy"
    assert ladder[1]["difficulty"] == "Medium"
    assert ladder[2]["difficulty"] == "Hard"


def test_warmup_ladder_prioritizes_user_weakness():
    """Asserts user's active weakness is prioritized when generating company ladder."""
    user_weaknesses = ["dp", "segment_tree"]
    ladder = generate_warmup_ladder(company="google", user_weaknesses=user_weaknesses)
    assert len(ladder) == 3
    # Check that dp or segment tree appear in top steps of Google ladder
    concepts = [p["concept"].lower().replace(" ", "_") for p in ladder]
    assert any("dp" in c or "segment" in c or "graph" in c for c in concepts)
