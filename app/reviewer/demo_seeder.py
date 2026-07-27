import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import CodeSubmission, ReviewResult, WeaknessRecord, ConceptTag, SubmissionConcept
from app.weakness.matcher import load_concept_index

DEMO_SNIPPETS = [
    {
        "title": "Two Sum Quadratic",
        "domain": "cp",
        "language": "python",
        "code": "def solve(nums, target):\n    n = len(nums)\n    for i in range(n):\n        for j in range(n):\n            if i != j and nums[i] + nums[j] == target:\n                return [i, j]\n    return []\n",
        "time": "O(N^2)",
        "score": 45,
        "issue": "Nested for loops scanning full array quadratic time",
        "fix": "Use hash map lookup for target - nums[i] in O(N)",
        "concepts": ["hash_map", "two_pointers"],
        "diff": "--- original.py\n+++ optimal_refactored.py\n@@ -1,7 +1,7 @@\n-def solve(nums, target):\n-    for i in range(len(nums)):\n-        for j in range(len(nums)):\n-            if nums[i] + nums[j] == target:\n-                return [i, j]\n+def solve(nums, target):\n+    seen = {}\n+    for i, num in enumerate(nums):\n+        if target - num in seen:\n+            return [seen[target - num], i]\n+        seen[num] = i\n"
    },
    {
        "title": "Three Sum Triple Loop",
        "domain": "cp",
        "language": "cpp",
        "code": "vector<vector<int>> threeSum(vector<int>& nums) {\n    vector<vector<int>> res;\n    int n = nums.size();\n    for(int i=0; i<n; i++) {\n        for(int j=i+1; j<n; j++) {\n            for(int k=j+1; k<n; k++) {\n                if(nums[i] + nums[j] + nums[k] == 0) {\n                    res.push_back({nums[i], nums[j], nums[k]});\n                }\n            }\n        }\n    }\n    return res;\n}\n",
        "time": "O(N^3)",
        "score": 35,
        "issue": "Triple nested loops algorithm yielding cubic time O(N^3)",
        "fix": "Sort array first, then use two pointers in O(N^2)",
        "concepts": ["two_pointers", "binary_search"],
        "diff": "--- original.cpp\n+++ optimal_refactored.cpp\n@@ -1,10 +1,15 @@\n vector<vector<int>> threeSum(vector<int>& nums) {\n+    sort(nums.begin(), nums.end());\n     vector<vector<int>> res;\n-    for(int i=0; i<n; i++) {\n-        for(int j=i+1; j<n; j++) {\n-            for(int k=j+1; k<n; k++) {\n-                if(nums[i] + nums[j] + nums[k] == 0) res.push_back({nums[i], nums[j], nums[k]});\n+    for(int i=0; i<nums.size(); i++) {\n+        if(i > 0 && nums[i] == nums[i-1]) continue;\n+        int l = i+1, r = nums.size()-1;\n+        while(l < r) {\n+            int sum = nums[i] + nums[l] + nums[r];\n+            if(sum == 0) { res.push_back({nums[i], nums[l], nums[r]}); l++; r--; }\n+            else if(sum < 0) l++;\n+            else r--;\n         }\n     }\n     return res;\n }\n"
    },
    {
        "title": "Sliding Window Max Slicing",
        "domain": "cp",
        "language": "python",
        "code": "def maxSlidingWindow(nums, k):\n    res = []\n    for i in range(len(nums) - k + 1):\n        res.append(max(nums[i:i+k]))\n    return res\n",
        "time": "O(N * K)",
        "score": 50,
        "issue": "Re-computing max over sub-slice on every window step O(N*K)",
        "fix": "Maintain monotonic deque for max element indices in O(N)",
        "concepts": ["sliding_window", "monotonic_stack"],
        "diff": "--- original.py\n+++ optimal_refactored.py\n@@ -1,5 +1,8 @@\n+from collections import deque\n def maxSlidingWindow(nums, k):\n+    q = deque()\n     res = []\n-    for i in range(len(nums) - k + 1):\n-        res.append(max(nums[i:i+k]))\n+    for i, n in enumerate(nums):\n+        while q and nums[q[-1]] <= n: q.pop()\n+        q.append(i)\n+        if q[0] == i - k: q.popleft()\n+        if i >= k - 1: res.append(nums[q[0]])\n     return res\n"
    },
    {
        "title": "Data Leakage Train Test Contamination",
        "domain": "ml",
        "language": "python",
        "code": "from sklearn.preprocessing import StandardScaler\nfrom sklearn.model_selection import train_test_split\n\nscaler = StandardScaler()\nX_scaled = scaler.fit_transform(X)\nX_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2)\n",
        "time": "O(N)",
        "score": 30,
        "issue": "Data Leakage: StandardScaler fit_transform on whole dataset before split",
        "fix": "Fit scaler ONLY on X_train, then transform X_test separately",
        "concepts": ["ml_leakage", "data_pipeline"],
        "diff": "--- original.py\n+++ optimal_refactored.py\n@@ -1,4 +1,4 @@\n-scaler = StandardScaler()\n-X_scaled = scaler.fit_transform(X)\n-X_train, X_test, y_train, y_test = train_test_split(X_scaled, y, test_size=0.2)\n+X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)\n+scaler = StandardScaler()\n+X_train = scaler.fit_transform(X_train)\n+X_test = scaler.transform(X_test)\n"
    },
    {
        "title": "Unseeded PyTorch Randomness",
        "domain": "ml",
        "language": "python",
        "code": "import torch\nimport numpy as np\n\ndef train_model(X, y):\n    weights = torch.randn(10, 5)\n    noise = np.random.rand(100)\n    return weights + noise\n",
        "time": "O(N)",
        "score": 40,
        "issue": "Non-reproducible training: PyTorch & NumPy random seeds not set",
        "fix": "Call torch.manual_seed(42) and np.random.seed(42)",
        "concepts": ["ml_leakage", "random_seed"],
        "diff": "--- original.py\n+++ optimal_refactored.py\n@@ -1,5 +1,7 @@\n+torch.manual_seed(42)\n+np.random.seed(42)\n def train_model(X, y):\n     weights = torch.randn(10, 5)\n     noise = np.random.rand(100)\n     return weights + noise\n"
    },
    {
        "title": "Metric Misuse On Training Set",
        "domain": "ml",
        "language": "python",
        "code": "from sklearn.metrics import accuracy_score\n\nmodel.fit(X_train, y_train)\ny_pred = model.predict(X_train)\nprint('Model Accuracy:', accuracy_score(y_train, y_pred))\n",
        "time": "O(N)",
        "score": 45,
        "issue": "Overfitting Risk: Accuracy evaluated on training set X_train instead of X_val",
        "fix": "Evaluate model accuracy on validation / holdout test set y_val",
        "concepts": ["ml_leakage", "metric_misuse"],
        "diff": "--- original.py\n+++ optimal_refactored.py\n@@ -1,3 +1,3 @@\n model.fit(X_train, y_train)\n-y_pred = model.predict(X_train)\n-print('Model Accuracy:', accuracy_score(y_train, y_pred))\n+y_pred = model.predict(X_val)\n+print('Validation Accuracy:', accuracy_score(y_val, y_pred))\n"
    },
    {
        "title": "Broadcasting Loss Mismatch",
        "domain": "ml",
        "language": "python",
        "code": "import torch\n\ndef compute_mse(y_pred, y_true):\n    # y_pred shape: (100, 1), y_true shape: (100,)\n    loss = (y_pred - y_true) ** 2\n    return loss.mean()\n",
        "time": "O(N^2)",
        "score": 35,
        "issue": "Broadcasting Mismatch: 2D (100,1) minus 1D (100,) creates (100,100) matrix",
        "fix": "Squeeze y_pred or reshape y_true to match dimensions before subtraction",
        "concepts": ["broadcasting_mismatch", "data_pipeline"],
        "diff": "--- original.py\n+++ optimal_refactored.py\n@@ -1,3 +1,3 @@\n def compute_mse(y_pred, y_true):\n-    loss = (y_pred - y_true) ** 2\n+    loss = (y_pred.squeeze() - y_true) ** 2\n     return loss.mean()\n"
    },
    {
        "title": "Error Swallowing Pass Block",
        "domain": "swe",
        "language": "python",
        "code": "def fetch_database_records(db_conn):\n    try:\n        records = db_conn.query('SELECT * FROM users')\n        return records\n    except:\n        pass\n    return []\n",
        "time": "O(N)",
        "score": 30,
        "issue": "Silent Failure: Bare except block swallows connection errors silently",
        "fix": "Catch specific DatabaseError exception and log traceback explicitly",
        "concepts": ["error_handling", "maintainability"],
        "diff": "--- original.py\n+++ optimal_refactored.py\n@@ -1,6 +1,7 @@\n def fetch_database_records(db_conn):\n     try:\n         records = db_conn.query('SELECT * FROM users')\n         return records\n-    except:\n-        pass\n+    except DatabaseError as err:\n+        logger.error(f'DB Fetch Failed: {err}')\n+        raise\n"
    },
    {
        "title": "Unclosed Connection Resource Leak",
        "domain": "swe",
        "language": "python",
        "code": "def parse_data_file(filepath):\n    f = open(filepath, 'r')\n    data = f.read()\n    return data.splitlines()\n",
        "time": "O(N)",
        "score": 40,
        "issue": "Resource Leak: File handle 'f' opened without context manager or close()",
        "fix": "Use 'with open(filepath) as f:' context manager for auto-cleanup",
        "concepts": ["resource_leak", "maintainability"],
        "diff": "--- original.py\n+++ optimal_refactored.py\n@@ -1,4 +1,3 @@\n def parse_data_file(filepath):\n-    f = open(filepath, 'r')\n-    data = f.read()\n-    return data.splitlines()\n+    with open(filepath, 'r') as f:\n+        return f.read().splitlines()\n"
    },
    {
        "title": "Mutable Default Argument Bug",
        "domain": "swe",
        "language": "python",
        "code": "def append_user_session(user_id, active_sessions=[]):\n    active_sessions.append(user_id)\n    return active_sessions\n",
        "time": "O(1)",
        "score": 35,
        "issue": "Shared State Bug: Default argument list [] persists across function calls",
        "fix": "Set default argument to None and initialize new list inside function body",
        "concepts": ["mutable_defaults", "maintainability"],
        "diff": "--- original.py\n+++ optimal_refactored.py\n@@ -1,3 +1,5 @@\n-def append_user_session(user_id, active_sessions=[]):\n+def append_user_session(user_id, active_sessions=None):\n+    if active_sessions is None:\n+        active_sessions = []\n     active_sessions.append(user_id)\n     return active_sessions\n"
    },
    {
        "title": "Fibonacci Exponential Recursion",
        "domain": "cp",
        "language": "python",
        "code": "def climbStairs(n):\n    if n <= 2:\n        return n\n    return climbStairs(n - 1) + climbStairs(n - 2)\n",
        "time": "O(2^N)",
        "score": 25,
        "issue": "Exponential Recursion TLE: Naive Fibonacci calls without memoization O(2^N)",
        "fix": "Use memoization or iterative DP in O(N)",
        "concepts": ["dp", "recursion"],
        "diff": "--- original.py\n+++ optimal_refactored.py\n@@ -1,4 +1,6 @@\n def climbStairs(n):\n-    if n <= 2: return n\n-    return climbStairs(n - 1) + climbStairs(n - 2)\n+    a, b = 1, 2\n+    for _ in range(n - 1):\n+        a, b = b, a + b\n+    return a\n"
    },
    {
        "title": "Coin Change Naive DFS",
        "domain": "cp",
        "language": "cpp",
        "code": "int coinChange(vector<int>& coins, int amount) {\n    if (amount == 0) return 0;\n    if (amount < 0) return -1;\n    int minCoins = INT_MAX;\n    for (int coin : coins) {\n        int res = coinChange(coins, amount - coin);\n        if (res >= 0) minCoins = min(minCoins, res + 1);\n    }\n    return minCoins == INT_MAX ? -1 : minCoins;\n}\n",
        "time": "O(2^N)",
        "score": 30,
        "issue": "Unmemoized Recursive Tree: Recomputing overlapping subproblems O(2^N)",
        "fix": "Build 1D DP table dp[amount] in O(amount * coins.size())",
        "concepts": ["dp", "recursion"],
        "diff": "--- original.cpp\n+++ optimal_refactored.cpp\n@@ -1,8 +1,7 @@\n int coinChange(vector<int>& coins, int amount) {\n-    if (amount == 0) return 0;\n-    if (amount < 0) return -1;\n-    int minCoins = INT_MAX;\n-    for (int coin : coins) {\n-        int res = coinChange(coins, amount - coin);\n-        if (res >= 0) minCoins = min(minCoins, res + 1);\n-    }\n+    vector<int> dp(amount + 1, amount + 1);\n+    dp[0] = 0;\n+    for(int i = 1; i <= amount; i++)\n+        for(int c : coins)\n+            if(i - c >= 0) dp[i] = min(dp[i], dp[i - c] + 1);\n+    return dp[amount] > amount ? -1 : dp[amount];\n"
    },
    {
        "title": "Merge K Sorted Lists Re-Sorting",
        "domain": "cp",
        "language": "java",
        "code": "public ListNode mergeKLists(ListNode[] lists) {\n    List<Integer> vals = new ArrayList<>();\n    for (ListNode node : lists) {\n        while (node != null) {\n            vals.add(node.val);\n            node = node.next;\n        }\n    }\n    Collections.sort(vals);\n    ListNode dummy = new ListNode(0), curr = dummy;\n    for (int val : vals) {\n        curr.next = new ListNode(val);\n        curr = curr.next;\n    }\n    return dummy.next;\n}\n",
        "time": "O(N log N)",
        "score": 55,
        "issue": "Suboptimal Re-sorting: Flattening and sorting all N nodes in O(N log N)",
        "fix": "Use PriorityQueue min-heap of k pointers in O(N log K)",
        "concepts": ["heap_priority_queue", "two_pointers"],
        "diff": "--- original.java\n+++ optimal_refactored.java\n@@ -1,8 +1,6 @@\n public ListNode mergeKLists(ListNode[] lists) {\n-    List<Integer> vals = new ArrayList<>();\n-    for (ListNode node : lists) while(node!=null) { vals.add(node.val); node = node.next; }\n-    Collections.sort(vals);\n+    PriorityQueue<ListNode> pq = new PriorityQueue<>((a,b)->a.val-b.val);\n+    for(ListNode l : lists) if(l != null) pq.add(l);\n     ListNode dummy = new ListNode(0), curr = dummy;\n-    for (int val : vals) { curr.next = new ListNode(val); curr = curr.next; }\n+    while(!pq.isEmpty()) { ListNode n = pq.poll(); curr.next = n; curr = curr.next; if(n.next!=null) pq.add(n.next); }\n     return dummy.next;\n }\n"
    },
    {
        "title": "Decoy Variable Name Detection",
        "domain": "cp",
        "language": "python",
        "code": "def solve(nums):\n    # Variable named hash_map is actually a list!\n    hash_map = []\n    for x in nums:\n        if x not in hash_map:\n            hash_map.append(x)\n    return hash_map\n",
        "time": "O(N^2)",
        "score": 40,
        "issue": "Decoy Name & O(N^2) Lookup: Variable named 'hash_map' is a list with linear x in hash_map lookup",
        "fix": "Use actual set() or dict for true O(1) hash table lookup",
        "concepts": ["hash_map", "maintainability"],
        "diff": "--- original.py\n+++ optimal_refactored.py\n@@ -1,5 +1,5 @@\n def solve(nums):\n-    hash_map = []\n-    for x in nums:\n-        if x not in hash_map: hash_map.append(x)\n-    return hash_map\n+    seen = set()\n+    for x in nums:\n+        if x not in seen: seen.add(x)\n+    return list(seen)\n"
    },
    {
        "title": "Decoy Recursion Function Name",
        "domain": "cp",
        "language": "python",
        "code": "def dfs_search(tree, target):\n    # Function named dfs_search but uses loop - no recursion\n    for node in tree:\n        if node == target:\n            return True\n    return False\n",

        "time": "O(N)",
        "score": 60,
        "issue": "Misleading Function Naming: Function is named 'dfs_search' but performs iterative scan",
        "fix": "Rename function to match iterative array scanning logic",
        "concepts": ["graph_traversal", "maintainability"],
        "diff": "--- original.py\n+++ optimal_refactored.py\n@@ -1,4 +1,4 @@\n-def dfs_search(tree, target):\n+def contains_target(tree, target):\n     for node in tree:\n         if node == target: return True\n     return False\n"
    }
]


async def seed_demo_submissions_for_user(db: AsyncSession, user_id: uuid.UUID) -> dict:
    """Seeds 15+ comprehensive bad code submissions into the database for live demonstration & stress testing."""
    concept_index = await load_concept_index(db)
    seeded_ids = []

    for item in DEMO_SNIPPETS:
        sub = CodeSubmission(
            user_id=user_id,
            domain=item["domain"],
            language=item["language"],
            problem_title=item["title"],
            code=item["code"],
        )
        db.add(sub)
        await db.commit()
        await db.refresh(sub)

        # Build ReviewResult
        rev = ReviewResult(
            submission_id=sub.id,
            time_complexity=item["time"],
            space_complexity="O(N)",
            score=item["score"],
            suggestions=[{
                "issue": item["issue"],
                "why": "AST syntax tree analysis & empirical sandbox curve fitting detected flaw.",
                "fix": item["fix"],
            }],
            better_approach=f"### Educational RAG Tutorial & Optimization Strategy\n\nTo optimize this `{item['title']}` solution, eliminate the quadratic or inefficient pattern by introducing **{', '.join(item['concepts'])}**.\n\n1. **Core Insight**: Instead of performing linear scans or redundant re-computations, store pre-calculated states or hash lookups.\n2. **Complexity Impact**: Reduces execution from `{item['time']}` down to optimal runtime bounds, enabling passing all test cases under 1.0s limit.",

            code_diff=item["diff"],
            concepts=item["concepts"],
            measured_complexity=item["time"],
            complexity_disagreement=False,
            complexity_warning="",
        )
        db.add(rev)
        await db.commit()

        # Link SubmissionConcept & WeaknessRecord
        for cname in item["concepts"]:
            tag = concept_index.get(cname)
            if tag:
                db.add(SubmissionConcept(
                    submission_id=sub.id,
                    concept_tag_id=tag.id,
                    was_flagged_as_gap=True,
                ))

                # Upsert WeaknessRecord
                result = await db.execute(
                    select(WeaknessRecord).where(
                        WeaknessRecord.user_id == user_id,
                        WeaknessRecord.concept_tag_id == tag.id,
                    )
                )
                wr = result.scalar_one_or_none()
                if not wr:
                    db.add(WeaknessRecord(
                        user_id=user_id,
                        concept_tag_id=tag.id,
                        gap_count=2,
                        last_flagged_at=datetime.now(timezone.utc),
                        is_active_weakness=True,
                    ))
                else:
                    wr.gap_count += 1
                    wr.is_active_weakness = True
                    wr.last_flagged_at = datetime.now(timezone.utc)

        await db.commit()
        seeded_ids.append(str(sub.id))

    return {
        "status": "success",
        "submissions_seeded": len(seeded_ids),
        "seeded_ids": seeded_ids,
        "message": f"Successfully seeded {len(seeded_ids)} bad code submissions across CP, ML, and SWE domains!",
    }
