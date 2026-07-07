import json
import re
from groq import Groq
from app.config import settings

client = Groq(api_key=settings.groq_api_key)

SYSTEM_PROMPT = """You are a world-class competitive programmer reviewing a student's DSA/CP code, in the style of a top competitive programmer explaining things clearly to someone learning.

You will receive:
1. The student's code
2. Structural facts already extracted from parsing (loop nesting depth, recursion, data structures detected)
3. Optionally, the problem statement

Your job: give a tutorial-style review. Be direct, precise, and educational — like a top-rated coder explaining WHY something is slow or suboptimal, not just that it is.

Respond with ONLY a valid JSON object, no markdown fences, no preamble, no explanation outside the JSON. Structure exactly as follows:

{
  "time_complexity": "e.g. O(n^2)",
  "space_complexity": "e.g. O(n)",
  "concepts": ["list", "of", "relevant CP/DSA concepts used or that SHOULD be used"],
  "suggestions": [
    {"issue": "short name of the issue", "why": "why this matters / what it costs", "fix": "concrete fix, name the exact technique or DS"}
  ],
  "better_approach": "A short tutorial-style paragraph (4-8 sentences) explaining the optimal approach, the key insight the student is missing, and how to think about this class of problem in the future.",
  "score": <integer 0-100, code quality + efficiency combined>
}

Rules:
- If the code is already optimal, say so plainly in better_approach and suggestions MUST be an empty list. Do not list suggestions if you are also claiming the approach is already optimal — these two fields must never contradict each other.
- If suggestions is non-empty, better_approach must NOT claim the code is already optimal — it must describe what the optimal approach actually looks like instead.
- Be specific: name exact data structures, algorithms, or techniques (e.g. "two-pointer", "monotonic stack", "binary search on answer"), not vague advice.
- Ground your complexity analysis using the structural facts given, but use your own judgment on the code itself too.
- Never pad suggestions with generic advice like "add comments" unless code quality genuinely suffers."""


def build_user_prompt(code: str, language: str, heuristics: dict, problem_title: str | None, problem_statement: str | None) -> str:
    parts = [f"Language: {language}", f"Structural facts (from static parsing): {json.dumps(heuristics)}"]
    if problem_title:
        parts.append(f"Problem: {problem_title}")
    if problem_statement:
        parts.append(f"Problem statement: {problem_statement}")
    parts.append(f"Code:\n```{language}\n{code}\n```")
    return "\n\n".join(parts)


def _extract_json(raw: str) -> dict:
    """Groq/LLMs sometimes wrap JSON in fences or add stray text despite instructions.
    Strip fences, then find the first {...} block and parse it."""
    cleaned = re.sub(r"```(?:json)?", "", raw).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if not match:
        raise ValueError("No JSON object found in LLM response")
    return json.loads(match.group(0))


def get_review(code: str, language: str, heuristics: dict, problem_title: str | None = None, problem_statement: str | None = None) -> dict:
    user_prompt = build_user_prompt(code, language, heuristics, problem_title, problem_statement)

    completion = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.3,
        max_tokens=1500,
    )

    raw_output = completion.choices[0].message.content
    parsed = _extract_json(raw_output)

    # defensive defaults in case model omits a field
    parsed.setdefault("time_complexity", None)
    parsed.setdefault("space_complexity", None)
    parsed.setdefault("concepts", [])
    parsed.setdefault("suggestions", [])
    parsed.setdefault("better_approach", None)
    parsed.setdefault("score", None)

    return parsed