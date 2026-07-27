# CP Hub — End-to-End Testing & LinkedIn Showcase Guide

This guide provides step-by-step instructions to test every feature of **CP Hub** locally and a copy-paste-ready LinkedIn post to publish and showcase your project.

---

## 1. Quick Local Launch

### Step 1: Backend Setup
```bash
# 1. Install dependencies
pip install -r app/requirements.txt

# 2. Configure .env file
cp .env.example .env
# Ensure DATABASE_URL points to Postgres (e.g. postgresql+asyncpg://postgres:postgres@localhost:5432/cphub)
# Ensure GROQ_API_KEY is populated

# 3. Apply database migrations
alembic upgrade head

# 4. Start FastAPI server
uvicorn app.main:app --reload --port 8000
```

### Step 2: Frontend Setup
```bash
cd frontend
npm install
npm run dev
# Opens at http://localhost:5173
```

### Step 3: Run Automated Test Suite
```bash
python -m pytest tests/ -v
# Runs all 21+ unit & integration tests
```

---

## 2. End-to-End Feature Verification Walkthrough

### Scenario 1: Codeforces History Import & Backfilling
1. Open dashboard at `http://localhost:5173`.
2. Click **Import Codeforces** button in the top right.
3. Enter handle `tourist` or `Benq` and click **Sync History**.
4. **Expected Result**: Submission history is imported from Codeforces public API, and active weaknesses are automatically backfilled on your radar chart and weakness list!

### Scenario 2: AST Call-Graph Recursion & Decoy Variable Protection
1. Go to **Reviewer** (`/reviewer`).
2. Paste decoy Python code:
   ```python
   def process_items(arr):
       mapValue = 5
       dict_data = 10
       return mapValue + dict_data
   ```
3. Submit review.
4. **Expected Result**: AST analyzer ignores `mapValue` and returns zero false-positive data structure hints!

### Scenario 3: Empirical Complexity Sandbox & Disagreement Banner
1. Submit known quadratic nested-loop solution:
   ```python
   def solve(arr):
       total = 0
       n = len(arr)
       for i in range(n):
           for j in range(n):
               total += arr[i] ^ arr[j]
       return total
   ```
2. **Expected Result**: Subprocess sandbox benchmarks execution across $N \in [100, 3000]$, fits curve to $O(N^2)$, and surfaces an **Empirical Benchmark Disagreement** banner if LLM output differs!

### Scenario 4: ML Data Leakage & Seed Diagnostics
1. Select domain **ML (Data Pipelines)** in the Reviewer.
2. Submit leaking code:
   ```python
   from sklearn.preprocessing import StandardScaler
   from sklearn.model_selection import train_test_split
   scaler = StandardScaler()
   X_scaled = scaler.fit_transform(X)
   X_train, X_test, y_train, y_test = train_test_split(X_scaled, y)
   ```
3. **Expected Result**: Flaw flagged: `Train/Test Data Leakage` — `.fit()` was called before split!

---

## 3. LinkedIn Post Copy (Ready to Publish 🚀)

Copy and paste the text below directly to LinkedIn:

---

**🔥 Introducing CP Hub — A Domain-Agnostic Code Diagnostic Engine with Empirical Verification**

Most code review tools tell you *what* went wrong once. Almost nobody tracks **why it keeps happening over time across submissions, per person**.

That longitudinal weakness signal is why I built **CP Hub**.

Unlike generic LLM wrappers or simple linters, CP Hub doesn't rely on unverified claims:

✨ **Key Highlights & Differentiators:**

1️⃣ **AST-Grounded Parsing (Scope-Aware)**: Scope-aware call-graph recursion checks & AST node declaration inspection across C++, Java, and Python — zero false positives from decoy variable names.
2️⃣ **Empirical Sandbox Complexity Verification**: Executes submitted code across scaling synthetic inputs ($N \in 10^2 - 10^5$), fitting growth curves ($O(N)$, $O(N \log N)$, $O(N^2)$) via log-log least squares regression to cross-check against LLM claims.
3️⃣ **Direct Codeforces Import**: One-click import via public API (`user.status`) to retroactively backfill personal weakness profiles from real contest history.
4️⃣ **Timed Resurfacing & Decay-on-Success**: 30-minute virtual contest reps with Codeforces-style decaying points. Successfully solving resurfaced problems decays weakness counters.
5️⃣ **Multi-Domain Extension (CP, ML & SWE)**: Specialized diagnostic analyzers for Competitive Programming, ML Data Pipeline Leakage (e.g., fitting scalers before train/test split), and SWE maintainability.
6️⃣ **Arq Background Job Queue**: High-throughput async job execution keeping request latency near-zero.

Built with **FastAPI (async)**, **Postgres**, **Tree-sitter**, **Groq / Llama 3.3 70B**, and **React / Vite**.

Check out the repo and let me know your thoughts! 👇

#CompetitiveProgramming #SoftwareEngineering #MachineLearning #FastAPI #Python #OpenSource #DeveloperTools #AI

---
