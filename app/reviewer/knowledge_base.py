"""Curated DSA/CP Concept Knowledge Base for grounded RAG retrieval and canonical diff generation."""

CONCEPT_KNOWLEDGE = {
    "hash_map": {
        "tag": "hash_map",
        "display_name": "Hash Map / Hashing",
        "explanation": "Hash tables map key-value pairs using a hash function, offering amortized O(1) time complexity for insertions, deletions, and lookups. In CP/OA prep, hash maps replace linear O(N) searches inside loops to reduce time complexity from O(N^2) to O(N).",
        "canonical_solution": """def two_sum(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []""",
        "common_mistakes": [
            "Using a Python list instead of set/dict for 'in' checks (linear O(N) instead of O(1)).",
            "Not handling hash collisions or unhashable types in custom data structures.",
            "Modifying dictionary keys during iteration."
        ]
    },
    "two_pointers": {
        "tag": "two_pointers",
        "display_name": "Two Pointers",
        "explanation": "The two-pointer technique uses two indices that traverse a sorted array or sequence simultaneously (often from opposite ends or at different speeds) to search for pairs or subsegments in O(N) time instead of O(N^2).",
        "canonical_solution": """def three_sum(nums):
    nums.sort()
    res = []
    for i in range(len(nums) - 2):
        if i > 0 and nums[i] == nums[i-1]:
            continue
        left, right = i + 1, len(nums) - 1
        while left < right:
            s = nums[i] + nums[left] + nums[right]
            if s == 0:
                res.append([nums[i], nums[left], nums[right]])
                while left < right and nums[left] == nums[left+1]: left += 1
                while left < right and nums[right] == nums[right-1]: right -= 1
                left += 1; right -= 1
            elif s < 0:
                left += 1
            else:
                right -= 1
    return res""",
        "common_mistakes": [
            "Forgetting to sort the array before applying left/right pointers.",
            "Missing duplicate element skip checks, leading to non-unique output triples.",
            "Off-by-one errors on boundary while loops (left <= right vs left < right)."
        ]
    },
    "sliding_window": {
        "tag": "sliding_window",
        "display_name": "Sliding Window",
        "explanation": "Sliding window maintains a dynamic range [left, right] over an array or string. As the right boundary expands, the left boundary shrinks whenever window constraints are violated, keeping subsegment processing to O(N) total time.",
        "canonical_solution": """def length_of_longest_substring(s: str) -> int:
    char_map = {}
    left = 0
    max_len = 0
    for right, char in enumerate(s):
        if char in char_map and char_map[char] >= left:
            left = char_map[char] + 1
        char_map[char] = right
        max_len = max(max_len, right - left + 1)
    return max_len""",
        "common_mistakes": [
            "Re-slicing strings or arrays inside the loop (e.g. s[left:right]), causing O(N^2) complexity.",
            "Failing to update left boundary index when duplicate character appears before current left.",
            "Not shrinking window until constraint is fully satisfied."
        ]
    },
    "binary_search": {
        "tag": "binary_search",
        "display_name": "Binary Search",
        "explanation": "Binary search halves the search space at each step by comparing target against middle element. Applies to sorted arrays or monotonic decision spaces ('binary search on answer') to achieve O(log N) time.",
        "canonical_solution": """def binary_search(nums, target):
    left, right = 0, len(nums) - 1
    while left <= right:
        mid = left + (right - left) // 2
        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            left = mid + 1
        else:
            right = mid - 1
    return -1""",
        "common_mistakes": [
            "Integer overflow during mid calculation in languages like C++/Java (`(left + right) / 2`).",
            "Infinite loops caused by incorrect boundary updates (`left = mid` instead of `left = mid + 1`).",
            "Applying binary search on unsorted collections without monotonic feasibility functions."
        ]
    },
    "dp": {
        "tag": "dp",
        "display_name": "Dynamic Programming",
        "explanation": "Dynamic Programming breaks problems into overlapping subproblems, storing optimal results in a memoization table or DP array. Transforms exponential O(2^N) recursive trees into polynomial O(N) or O(N*W) state solutions.",
        "canonical_solution": """def coin_change(coins, amount):
    dp = [float('inf')] * (amount + 1)
    dp[0] = 0
    for coin in coins:
        for x in range(coin, amount + 1):
            dp[x] = min(dp[x], dp[x - coin] + 1)
    return dp[amount] if dp[amount] != float('inf') else -1""",
        "common_mistakes": [
            "Omitting base cases in recursion (e.g., dp[0] = 0).",
            "Incorrect state iteration order in 1D vs 2D knapsack DP.",
            "Exponential recursion without `@lru_cache` or explicit DP table."
        ]
    },
    "graph_traversal": {
        "tag": "graph_traversal",
        "display_name": "Graph Traversal (BFS/DFS)",
        "explanation": "Graph algorithms explore vertices and edges using Breadth-First Search (queue for shortest unweighted paths) or Depth-First Search (stack/recursion for connected components, topological ordering, and cycle detection).",
        "canonical_solution": """from collections import deque

def num_islands(grid):
    if not grid: return 0
    rows, cols = len(grid), len(grid[0])
    islands = 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == "1":
                islands += 1
                queue = deque([(r, c)])
                grid[r][c] = "0"
                while queue:
                    curr_r, curr_c = queue.popleft()
                    for dr, dc in [(-1,0), (1,0), (0,-1), (0,1)]:
                        nr, nc = curr_r + dr, curr_c + dc
                        if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == "1":
                            grid[nr][nc] = "0"
                            queue.append((nr, nc))
    return islands""",
        "common_mistakes": [
            "Forgetting to mark nodes as visited upon enqueueing in BFS, causing infinite loops and MLE.",
            "Recursion depth limit exceeded in DFS on deep graph structures in Python.",
            "Not handling disconnected graph components."
        ]
    },
    "monotonic_stack": {
        "tag": "monotonic_stack",
        "display_name": "Monotonic Stack",
        "explanation": "A monotonic stack maintains elements in strictly increasing or decreasing order. It solves Next Greater Element and histogram area problems in linear O(N) time because each index is pushed and popped at most once.",
        "canonical_solution": """def daily_temperatures(temperatures):
    n = len(temperatures)
    ans = [0] * n
    stack = []  # stores indices
    for i in range(n):
        while stack and temperatures[i] > temperatures[stack[-1]]:
            prev_idx = stack.pop()
            ans[prev_idx] = i - prev_idx
        stack.append(i)
    return ans""",
        "common_mistakes": [
            "Storing values instead of indices in stack when distance/width calculations are required.",
            "Using wrong inequality (< vs <=) causing duplicate value handling issues."
        ]
    },
    "heap_priority_queue": {
        "tag": "heap_priority_queue",
        "display_name": "Heap / Priority Queue",
        "explanation": "Priority queues maintain dynamic min/max elements in O(log N) push/pop operations. Essential for Kth largest elements, continuous median tracking, and Dijkstra's algorithm.",
        "canonical_solution": """import heapq

def find_kth_largest(nums, k):
    min_heap = []
    for num in nums:
        heapq.heappush(min_heap, num)
        if len(min_heap) > k:
            heapq.heappop(min_heap)
    return min_heap[0]""",
        "common_mistakes": [
            "Using Python's default min-heap when max-heap behavior is needed (forgetting sign negation `-val`).",
            "Pushing full arrays into heap without maintaining size K, resulting in O(N log N) instead of O(N log K)."
        ]
    },
    "greedy": {
        "tag": "greedy",
        "display_name": "Greedy",
        "explanation": "Greedy algorithms make locally optimal choices at each step, proving globally optimal for problems with greedy choice property and optimal substructure (e.g. interval scheduling, activity selection).",
        "canonical_solution": """def erase_overlap_intervals(intervals):
    if not intervals: return 0
    intervals.sort(key=lambda x: x[1])
    count = 0
    last_end = float('-inf')
    for start, end in intervals:
        if start >= last_end:
            last_end = end
        else:
            count += 1
    return count""",
        "common_mistakes": [
            "Sorting by start time instead of end time in interval overlap problems.",
            "Applying greedy heuristics without verifying optimal substructure proof."
        ]
    },
    "backtracking": {
        "tag": "backtracking",
        "display_name": "Backtracking",
        "explanation": "Backtracking explores all candidate solutions by incrementally building states and aborting (pruning) paths as soon as candidates cannot produce valid results (N-Queens, Permutations, Sudoku).",
        "canonical_solution": """def permute(nums):
    res = []
    def backtrack(curr, remaining):
        if not remaining:
            res.append(list(curr))
            return
        for i in range(len(remaining)):
            backtrack(curr + [remaining[i]], remaining[:i] + remaining[i+1:])
    backtrack([], nums)
    return res""",
        "common_mistakes": [
            "Appending mutable list references (`res.append(curr)`) without creating a shallow copy (`curr.copy()`).",
            "Missing path undo steps (backtracking reset) when reusing state arrays."
        ]
    },
    "union_find": {
        "tag": "union_find",
        "display_name": "Union-Find / DSU",
        "explanation": "Disjoint Set Union (DSU) tracks partitioned sets across elements in near-O(1) amortized time using path compression and union by rank.",
        "canonical_solution": """class DSU:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n
    def find(self, i):
        if self.parent[i] == i:
            return i
        self.parent[i] = self.find(self.parent[i])  # Path compression
        return self.parent[i]
    def union(self, i, j):
        root_i, root_j = self.find(i), self.find(j)
        if root_i != root_j:
            if self.rank[root_i] < self.rank[root_j]:
                root_i, root_j = root_j, root_i
            self.parent[root_j] = root_i
            if self.rank[root_i] == self.rank[root_j]:
                self.rank[root_i] += 1
            return True
        return False""",
        "common_mistakes": [
            "Forgetting path compression inside `find()`.",
            "Not handling self-loops or non-integer node labels."
        ]
    },
    "prefix_sum": {
        "tag": "prefix_sum",
        "display_name": "Prefix Sum",
        "explanation": "Prefix sum arrays precompute cumulative sums so range sum queries `sum(L, R)` run in O(1) time.",
        "canonical_solution": """def subarray_sum(nums, k):
    count = 0
    curr_sum = 0
    prefix_counts = {0: 1}
    for num in nums:
        curr_sum += num
        if curr_sum - k in prefix_counts:
            count += prefix_counts[curr_sum - k]
        prefix_counts[curr_sum] = prefix_counts.get(curr_sum, 0) + 1
    return count""",
        "common_mistakes": [
            "Forgetting to initialize `{0: 1}` in prefix map for subarrays starting at index 0.",
            "Off-by-one errors when indexing 1D prefix sum arrays."
        ]
    },
    "bit_manipulation": {
        "tag": "bit_manipulation",
        "display_name": "Bit Manipulation",
        "explanation": "Bitwise operations (AND, OR, XOR, shifts) operate directly on binary bits in O(1) constant time.",
        "canonical_solution": """def single_number(nums):
    result = 0
    for num in nums:
        result ^= num
    return result""",
        "common_mistakes": [
            "Operator precedence bugs (e.g. `a & b == 0` evaluated as `a & (b == 0)`).",
            "Not handling negative integer sign extension in fixed-width languages."
        ]
    },
    "trie": {
        "tag": "trie",
        "display_name": "Trie",
        "explanation": "A Trie (prefix tree) stores string keys node-by-node, enabling O(L) prefix search where L is word length.",
        "canonical_solution": """class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False

class Trie:
    def __init__(self):
        self.root = TrieNode()
    def insert(self, word: str):
        node = self.root
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.root if False else node.children[char]
        node.is_end = True""",
        "common_mistakes": [
            "Confusing prefix search with full word search (`is_end` check missing).",
            "Unbounded memory growth on large dictionaries."
        ]
    },
    "segment_tree": {
        "tag": "segment_tree",
        "display_name": "Segment Tree",
        "explanation": "Segment Trees support O(log N) point updates and range query aggregations (sum, min, max, GCD).",
        "canonical_solution": """class NumArray:
    def __init__(self, nums):
        self.n = len(nums)
        self.tree = [0] * (2 * self.n)
        for i in range(self.n):
            self.tree[self.n + i] = nums[i]
        for i in range(self.n - 1, 0, -1):
            self.tree[i] = self.tree[2 * i] + self.tree[2 * i + 1]

    def update(self, index: int, val: int):
        pos = index + self.n
        self.tree[pos] = val
        while pos > 1:
            pos //= 2
            self.tree[pos] = self.tree[2 * pos] + self.tree[2 * pos + 1]""",
        "common_mistakes": [
            "Allocating array of size 2*N or 4*N incorrectly.",
            "Off-by-one errors on 1-based tree indexing."
        ]
    }
}
