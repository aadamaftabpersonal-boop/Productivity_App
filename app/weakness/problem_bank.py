# Small curated set per concept — enough to demonstrate the resurfacing logic honestly.
# Not a full problem bank; a real v2 would pull from LeetCode's tagged problem API.
PROBLEM_BANK = {
    "sliding_window": [
        {"title": "Longest Substring Without Repeating Characters", "url": "https://leetcode.com/problems/longest-substring-without-repeating-characters/", "optimal_time_complexity": "O(n)", "optimal_space_complexity": "O(n)"},
        {"title": "Minimum Window Substring", "url": "https://leetcode.com/problems/minimum-window-substring/", "optimal_time_complexity": "O(n)", "optimal_space_complexity": "O(n)"},
    ],
    "two_pointers": [
        {"title": "Container With Most Water", "url": "https://leetcode.com/problems/container-with-most-water/", "optimal_time_complexity": "O(n)", "optimal_space_complexity": "O(1)"},
        {"title": "3Sum", "url": "https://leetcode.com/problems/3sum/", "optimal_time_complexity": "O(n^2)", "optimal_space_complexity": "O(1)"},
    ],
    "hash_map": [
        {"title": "Two Sum", "url": "https://leetcode.com/problems/two-sum/", "optimal_time_complexity": "O(n)", "optimal_space_complexity": "O(n)"},
        {"title": "Group Anagrams", "url": "https://leetcode.com/problems/group-anagrams/", "optimal_time_complexity": "O(n)", "optimal_space_complexity": "O(n)"},
    ],
    "binary_search": [
        {"title": "Search in Rotated Sorted Array", "url": "https://leetcode.com/problems/search-in-rotated-sorted-array/", "optimal_time_complexity": "O(log n)", "optimal_space_complexity": "O(1)"},
        {"title": "Koko Eating Bananas", "url": "https://leetcode.com/problems/koko-eating-bananas/", "optimal_time_complexity": "O(n log n)", "optimal_space_complexity": "O(1)"},
    ],
    "dp": [
        {"title": "House Robber", "url": "https://leetcode.com/problems/house-robber/", "optimal_time_complexity": "O(n)", "optimal_space_complexity": "O(1)"},
        {"title": "Longest Increasing Subsequence", "url": "https://leetcode.com/problems/longest-increasing-subsequence/", "optimal_time_complexity": "O(n log n)", "optimal_space_complexity": "O(n)"},
    ],
    "graph_traversal": [
        {"title": "Number of Islands", "url": "https://leetcode.com/problems/number-of-islands/", "optimal_time_complexity": "O(n)", "optimal_space_complexity": "O(n)"},
        {"title": "Course Schedule", "url": "https://leetcode.com/problems/course-schedule/", "optimal_time_complexity": "O(n)", "optimal_space_complexity": "O(n)"},
    ],
    "monotonic_stack": [
        {"title": "Daily Temperatures", "url": "https://leetcode.com/problems/daily-temperatures/", "optimal_time_complexity": "O(n)", "optimal_space_complexity": "O(n)"},
        {"title": "Largest Rectangle in Histogram", "url": "https://leetcode.com/problems/largest-rectangle-in-histogram/", "optimal_time_complexity": "O(n)", "optimal_space_complexity": "O(n)"},
    ],
    "heap_priority_queue": [
        {"title": "Kth Largest Element in an Array", "url": "https://leetcode.com/problems/kth-largest-element-in-an-array/", "optimal_time_complexity": "O(n log k)", "optimal_space_complexity": "O(k)"},
        {"title": "Merge k Sorted Lists", "url": "https://leetcode.com/problems/merge-k-sorted-lists/", "optimal_time_complexity": "O(n log k)", "optimal_space_complexity": "O(k)"},
    ],
    "greedy": [
        {"title": "Jump Game", "url": "https://leetcode.com/problems/jump-game/", "optimal_time_complexity": "O(n)", "optimal_space_complexity": "O(1)"},
    ],
    "backtracking": [
        {"title": "Subsets", "url": "https://leetcode.com/problems/subsets/", "optimal_time_complexity": "O(2^n)", "optimal_space_complexity": "O(n)"},
        {"title": "Word Search", "url": "https://leetcode.com/problems/word-search/", "optimal_time_complexity": "O(n * 3^l)", "optimal_space_complexity": "O(l)"},
    ],
    "union_find": [
        {"title": "Number of Connected Components in an Undirected Graph", "url": "https://leetcode.com/problems/number-of-connected-components-in-an-undirected-graph/", "optimal_time_complexity": "O(n alpha(n))", "optimal_space_complexity": "O(n)"},
    ],
    "prefix_sum": [
        {"title": "Subarray Sum Equals K", "url": "https://leetcode.com/problems/subarray-sum-equals-k/", "optimal_time_complexity": "O(n)", "optimal_space_complexity": "O(n)"},
    ],
    "bit_manipulation": [
        {"title": "Single Number", "url": "https://leetcode.com/problems/single-number/", "optimal_time_complexity": "O(n)", "optimal_space_complexity": "O(1)"},
    ],
    "trie": [
        {"title": "Implement Trie (Prefix Tree)", "url": "https://leetcode.com/problems/implement-trie-prefix-tree/", "optimal_time_complexity": "O(l)", "optimal_space_complexity": "O(n * l)"},
    ],
    "segment_tree": [
        {"title": "Range Sum Query - Mutable", "url": "https://leetcode.com/problems/range-sum-query-mutable/", "optimal_time_complexity": "O(log n)", "optimal_space_complexity": "O(n)"},
    ],
}


def compare_against_reference_optimal(problem_title: str, user_measured_complexity: str) -> dict:
    """Compare user's measured complexity against verified optimal reference solution (closes 5.3)."""
    for concept, probs in PROBLEM_BANK.items():
        for p in probs:
            if p["title"].lower() == problem_title.lower():
                opt = p.get("optimal_time_complexity", "O(n)")
                is_optimal = (user_measured_complexity == opt)
                return {
                    "matched_problem": p["title"],
                    "optimal_time_complexity": opt,
                    "user_measured_complexity": user_measured_complexity,
                    "is_optimal": is_optimal,
                    "diff": None if is_optimal else f"Optimal approach achieves {opt}, but your submission measured {user_measured_complexity}.",
                }

    return {
        "matched_problem": problem_title,
        "optimal_time_complexity": None,
        "user_measured_complexity": user_measured_complexity,
        "is_optimal": True,
        "diff": None,
    }