# Known Issues

Tracked honestly, including ones already fixed, so the history of what was
wrong and when it got fixed stays visible rather than quietly disappearing.

## Fixed

### BUG-001: Event loop blocked during LLM review call
**Status: Fixed** (see commit that introduces `AsyncGroq`)

`get_review()` in `app/reviewer/llm_review.py` called the synchronous Groq
SDK client (`Groq`) directly inside an `async def` FastAPI route
(`app/routers/reviewer.py`). Since the call was never awaited (nothing to
await — it wasn't a coroutine), it ran synchronously on the request-handling
thread, blocking the single event loop for the full duration of the LLM
call. In practice: while one person's review was being generated, the
server could not serve *any* other request — no other user's login, no
health check, nothing — because FastAPI/uvicorn serve everything off that
one loop.

This directly contradicted the "async FastAPI backend" architecture claim on
its single most expensive, most frequently-hit code path.

**Fix**: switched to Groq's `AsyncGroq` client, made `get_review` an
`async def`, and awaited it properly at the call site.

**Regression test**: `tests/test_reviewer_concurrency.py`. Getting this test
to actually discriminate fixed-vs-buggy code took three attempts — see the
design note in that file. The short version: an in-process test client and
even a naive live-server test can both give false confidence, because there
are legitimate `await` points elsewhere in the handler that let a concurrent
request sneak through regardless of whether the specific line under test
blocks. The working version uses an explicit cross-thread signal fired the
instant execution enters the mocked call, so the "fast" concurrent request
is guaranteed to be launched during the exact window that matters.

### ISSUE-002: Real AST call-graph recursion & node type inspection
**Status: Fixed**

Replaced naive substring counting in `_detect_recursion` with scope-aware AST call-graph walking (extracting declared function names and matching `call` / `call_expression` / `method_invocation` callee identifiers). Replaced raw identifier keyword string matching in `_detect_data_structures` with AST type/declaration/constructor node inspection (`template_type` / `type_identifier` / `generic_type` / call nodes) across Python, C++, and Java. Decoy identifiers like `mapValue` or `solve_helper` no longer trigger false positive data structure hints or recursion flags.

**Regression test**: `tests/test_tree_analysis.py`.

### ISSUE-003: Empirical complexity verification & sandboxed execution
**Status: Fixed**

Implemented a sandboxed execution harness (`app/reviewer/complexity_sandbox.py`) that runs submitted code across synthetic inputs at multiple sizes ($N \in [10^2, 3 \cdot 10^3]$), fits timing data to canonical growth curves via log-log least squares regression, and cross-checks the empirical fit against the LLM's claimed complexity. Disagreements trigger an explicit warning surfacing both measured growth and LLM claim to the user.

**Regression test**: `tests/test_complexity_sandbox.py`.

### ISSUE-004: Async background job queue with Arq
**Status: Fixed**

Implemented `arq` background job pipeline (`app/jobs/queue.py`) for processing submission reviews and empirical execution benchmarks asynchronously without blocking interactive request latency. Submitting code returns HTTP 202 Accepted with a job ID, and job status is pollable via `/reviewer/job/{job_id}`.

**Regression test**: `tests/test_jobs.py`.

### ISSUE-005: Rate limiting on auth endpoints
**Status: Fixed**

Added `slowapi` IP/account token-bucket rate limiters on `/auth/login` (15/min), `/auth/register` (10/min), and `/auth/refresh` (30/min).

### ISSUE-006: Input size & sanitization limit on submitted code
**Status: Fixed**

Enforced a 64KB (`65536` bytes) input size limit on submitted code payloads prior to AST parsing or background review pipeline execution. Oversized inputs are rejected immediately with HTTP 400 Bad Request.

### ISSUE-007: Domain scope narrowed to cp/swe; ML pipeline analyzer removed
**Status: Fixed**

Domain scope narrowed exclusively to CP (Algorithms) and SWE (Maintainability) to align strictly with the OA Prep Helper product thesis. Removed `app/domains/ml.py` and `tests/test_ml_analyzer.py`. Updated routers and frontend dropdown selectors to allow only `"cp"` and `"swe"` domains. Existing database records with `domain = 'ml'` remain preserved to prevent historical read crashes.

### ISSUE-008: Real RAG retrieval replacing prompt that falsely claimed RAG
**Status: Fixed**

Replaced ungrounded LLM review prompts with real in-memory RAG retrieval (`app/reviewer/rag_index.py` & `app/reviewer/knowledge_base.py`). System prompt and user prompt now ground reviews strictly in retrieved canonical solutions, common mistakes, and algorithm explanations.

**Regression test**: `tests/test_rag_retrieval.py`.

### ISSUE-009: Diff generator wrong-fallback bug fixed
**Status: Fixed**

`diff_generator.py` previously fell back to a hardcoded Two Sum solution whenever LLM diff generation timed out or failed. Replaced hardcoded Two Sum stubs with `retrieved[0]["canonical_solution"]` when available, or a clean non-misleading patch header.

**Regression test**: `tests/test_rag_retrieval.py`.

### ISSUE-010: Instant pre-flight anti-bug checklist added to tree-sitter parser pipeline
**Status: Fixed**

Added `app/reviewer/preflight.py` to turn tree-sitter AST heuristics into instant pre-submission warnings (`integer_overflow_risk`, `fast_io_endl`, `fast_io_missing_sync`, `unbounded_recursion_risk`) in the synchronous submit response path.

**Regression test**: `tests/test_preflight.py`.

## Open

*(No open issues remaining in Phase 0 queue.)*




