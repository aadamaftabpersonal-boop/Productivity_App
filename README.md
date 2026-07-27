# CP Hub

A diagnostic tool for competitive programmers: submit code, get an AST-informed,
LLM-backed review (complexity, patterns used, concept tags), and track which
concepts you systematically get wrong over time.

**Not** a course platform or DSA-lessons app. The scope is intentionally narrow:
diagnose what you're actually doing in your submissions, not teach content.

## Status

This project is under active, staged improvement. See `BUGS.md` for known
issues and their fix status, and the project bible (kept outside this repo)
for the full phased roadmap.

## Stack

- **Backend**: FastAPI (async), SQLAlchemy 2.0 (async, asyncpg), Alembic
- **Auth**: JWT access + refresh tokens, with refresh-token rotation and
  reuse detection (a replayed, already-rotated refresh token revokes the
  entire token family, not just itself)
- **Code analysis**: tree-sitter for structural facts (loop nesting depth,
  function boundaries, syntax validity), feeding an LLM (Groq / Llama 3.3 70B)
  for the actual review
- **Frontend**: (see `/frontend`)

## Known, honestly-documented limitations (as of this commit)

- AST structural analysis parses loop nesting depth, syntax validity, scope-aware call-graph recursion, and type/declaration/constructor nodes for data structures (Python, C++, Java).
- Complexity claims in a review are currently LLM output with no independent
  verification. An empirical scaling-test cross-check is planned but not
  yet built.
- No production usage data yet — this has not been used by real CP students
  beyond the author's own testing.

## Running locally

```bash
pip install -r app/requirements.txt
cp .env.example .env  # fill in DATABASE_URL, JWT_SECRET_KEY, GROQ_API_KEY
alembic upgrade head
uvicorn app.main:app --reload
```

## Running tests

Tests run against a real Postgres instance (not SQLite/mocks) — the models
use Postgres-specific column types, and the concurrency regression test
specifically needs to reflect real async driver behavior.

```bash
# requires a local Postgres with a cphub_test database/role, matching .env
pytest tests/ -v
```

See `tests/test_reviewer_concurrency.py` for a detailed design note on why
that particular test went through three iterations before it actually
discriminated fixed vs. buggy code — worth reading if you're writing
concurrency tests elsewhere in this codebase.

## Architecture notes

- `app/security.py` / `app/routers/auth.py` — JWT issuance, refresh rotation,
  reuse-detection-revokes-family logic
- `app/reviewer/tree_analysis.py` — tree-sitter structural analysis
- `app/reviewer/llm_review.py` — LLM review call (async Groq client — see
  `BUGS.md` for why this matters)
- `app/weakness/matcher.py` — concept-tag weakness tracking; uses explicit
  keyword/alias matching rather than embeddings by design (see the comment
  in that file for the tradeoff reasoning)
