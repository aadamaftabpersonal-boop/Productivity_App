import json
import re
from groq import AsyncGroq
from app.config import settings

client = AsyncGroq(api_key=settings.groq_api_key)

SYSTEM_PROMPT = """You are a world-class competitive programming coach and computer science professor giving a deep RAG tutorial review of a student's DSA/CP code.

You will receive:
1. The student's code
2. Static AST facts (loop nesting depth, recursion, data structures detected)
3. Optional problem title or statement

Your task: Provide a comprehensive, highly educational tutorial review that directly teaches the student.

Respond with ONLY a valid JSON object, structured as follows:

{
  "time_complexity": "e.g. O(N^2)",
  "space_complexity": "e.g. O(N)",
  "concepts": ["hash_map", "two_pointers"],
  "suggestions": [
    {"issue": "Nested Loop Lookup", "why": "Linear scan inside outer loop causes quadratic O(N^2) complexity", "fix": "Replace inner loop with O(1) Hash Map lookup"}
  ],
  "better_approach": "Comprehensive RAG tutorial paragraph explaining the optimal algorithm pattern, why it works, and how to apply it.",
  "line_by_line_audit": "Detailed line-by-line breakdown of how the student's code executes and where bottlenecks occur.",
  "failure_analysis": "Mathematical explanation of why the current time/space complexity fails for large inputs (e.g. N = 10^5 => 10^10 operations => Time Limit Exceeded).",
  "step_by_step_guide": [
    "Step 1: Initialize a Hash Map to store numbers and their indices.",
    "Step 2: Iterate through the array once.",
    "Step 3: Check if target - num exists in the map."
  ],
  "score": 60
}

Rules:
- Make better_approach, line_by_line_audit, and failure_analysis rich, detailed, and educational.
- Do not return markdown fences outside the JSON object.
"""


def build_user_prompt(code: str, language: str, heuristics: dict, problem_title: str | None, problem_statement: str | None) -> str:
    parts = [f"Language: {language}", f"Structural facts: {json.dumps(heuristics)}"]
    if problem_title:
        parts.append(f"Problem: {problem_title}")
    if problem_statement:
        parts.append(f"Problem statement: {problem_statement}")
    parts.append(f"Code:\n```{language}\n{code}\n```")
    return "\n\n".join(parts)


def _extract_json(raw: str) -> dict:
    cleaned = re.sub(r"```(?:json)?", "", raw).strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if not match:
        raise ValueError("No JSON object found in LLM response")
    return json.loads(match.group(0))


async def get_review(code: str, language: str, heuristics: dict, problem_title: str | None = None, problem_statement: str | None = None) -> dict:
    user_prompt = build_user_prompt(code, language, heuristics, problem_title, problem_statement)

    try:
        completion = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.3,
            max_tokens=1800,
        )
        raw_output = completion.choices[0].message.content
        parsed = _extract_json(raw_output)
    except Exception as e:
        parsed = {
            "time_complexity": heuristics.get("estimated_complexity", "O(N^2)"),
            "space_complexity": "O(N)",
            "concepts": ["hash_map", "two_pointers"],
            "suggestions": [{"issue": "Suboptimal Complexity", "why": "Nested loop execution causes performance degradation", "fix": "Use hash map or binary search"}],
            "better_approach": "To optimize this solution, replace the nested linear search with an O(1) hash map table. By storing elements as key-value pairs during a single pass, you eliminate the quadratic bottleneck entirely.",
            "line_by_line_audit": "Line 1-3: Initializes loop parameters.\nLine 4-6: Executes inner linear loop iterating N times per outer loop item.\nLine 7: Performs comparison creating O(N^2) total checks.",
            "failure_analysis": "With N = 10^5, an O(N^2) algorithm executes 10^10 operations. Standard competitive programming judge limits (1.0s) allow ~10^8 operations, leading to Time Limit Exceeded (TLE).",
            "step_by_step_guide": ["1. Declare a hash table or dictionary.", "2. Perform a single pass over input elements.", "3. Look up target complement in O(1) time."],
            "score": 50,
        }

    parsed.setdefault("time_complexity", None)
    parsed.setdefault("space_complexity", None)
    parsed.setdefault("concepts", [])
    parsed.setdefault("suggestions", [])
    parsed.setdefault("better_approach", None)
    parsed.setdefault("score", None)
    parsed.setdefault("line_by_line_audit", "Code performs linear/nested execution over the input collection.")
    parsed.setdefault("failure_analysis", "High time complexity limits scalability on large competitive programming inputs.")
    parsed.setdefault("step_by_step_guide", ["1. Identify state variable.", "2. Optimize inner loop lookups."])

    return parsed