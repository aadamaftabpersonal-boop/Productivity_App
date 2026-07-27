"""Company-Style Warm-Up Ladder Generator module.

Generates a custom 3-problem warm-up sequence (Easy -> Medium -> Hard) matching company-specific
topic distributions and prioritizing the user's active weakness gaps.
"""
from typing import List, Dict, Any
from app.weakness.taxonomy import CURATED_PROBLEMS_BY_CONCEPT

COMPANY_PROFILES = {
    "meta": ["two_pointers", "binary_search", "hash_map", "prefix_sum"],
    "amazon": ["sliding_window", "heap_priority_queue", "graph_traversal", "hash_map"],
    "google": ["dp", "graph_traversal", "segment_tree", "binary_search"],
    "uber": ["monotonic_stack", "prefix_sum", "graph_traversal", "two_pointers"],
}


def generate_warmup_ladder(company: str, user_weaknesses: List[str] = None) -> List[Dict[str, Any]]:
    """Generates a 3-problem ladder tailored to the company and user's weakness profile."""
    company_key = company.lower()
    pref_topics = COMPANY_PROFILES.get(company_key, COMPANY_PROFILES["meta"])

    # Prioritize user weaknesses that overlap with company preferred topics
    user_weaknesses = user_weaknesses or []
    weakness_keys = [w.lower().replace(" ", "_") for w in user_weaknesses]

    ordered_topics = []
    # 1. Overlapping weakness & company topics
    for t in pref_topics:
        if t in weakness_keys:
            ordered_topics.append(t)
    # 2. Remaining company topics
    for t in pref_topics:
        if t not in ordered_topics:
            ordered_topics.append(t)
    # 3. All other taxonomy topics
    for t in CURATED_PROBLEMS_BY_CONCEPT.keys():
        if t not in ordered_topics:
            ordered_topics.append(t)

    ladder = []
    difficulties = ["Easy", "Medium", "Hard"]

    for idx, difficulty in enumerate(difficulties):
        chosen_problem = None
        for topic in ordered_topics:
            probs = CURATED_PROBLEMS_BY_CONCEPT.get(topic, [])
            for p in probs:
                if p["difficulty"] == difficulty and p not in ladder:
                    chosen_problem = {
                        "step": idx + 1,
                        "difficulty": difficulty,
                        "concept": topic.replace("_", " ").title(),
                        "title": p["title"],
                        "url": p["url"],
                        "target_time_minutes": 15 if difficulty == "Easy" else (25 if difficulty == "Medium" else 35),
                    }
                    break
            if chosen_problem:
                break

        if not chosen_problem:
            chosen_problem = {
                "step": idx + 1,
                "difficulty": difficulty,
                "concept": "General Algorithm",
                "title": f"LeetCode {difficulty} Warm-Up Problem",
                "url": f"https://leetcode.com/problemset/all/?difficulty={difficulty.upper()}",
                "target_time_minutes": 20,
            }
        ladder.append(chosen_problem)

    return ladder
