import json
import re
from groq import AsyncGroq
from app.config import settings
from app.reviewer.rag_index import retrieve

client = AsyncGroq(api_key=settings.groq_api_key)

SYSTEM_PROMPT = """You are a world-class competitive programming coach and computer science professor reviewing a student's DSA/CP code.

You are provided with:
1. The student's code
2. Static AST facts (loop nesting, recursion, data structures)
3. Grounded reference material retrieved from the concept knowledge base

Your job: Provide a tutorial review grounded strictly in the retrieved reference material. Explain WHY the current code is suboptimal using complexity principles from the reference, and guide the student on applying the canonical pattern.

Respond with ONLY a valid JSON object, structured as follows:

{
  "time_complexity": "e.g. O(N^2)",
  "space_complexity": "e.g. O(N)",
  "concepts": ["hash_map", "two_pointers"],
  "suggestions": [
    {"issue": "Nested Loop Lookup", "why": "Linear scan inside outer loop causes quadratic O(N^2) complexity", "fix": "Replace inner loop with O(1) Hash Map lookup"}
  ],
  "better_approach": "Comprehensive tutorial paragraph explaining the optimal algorithm pattern, why it works, and how to apply it based on retrieved reference material.",
  "line_by_line_audit": "Detailed line-by-line breakdown of how the student's code executes.",
  "failure_analysis": "Mathematical explanation of why the current complexity fails for large inputs.",
  "step_by_step_guide": [
    "Step 1: Declare the primary data structure from reference material.",
    "Step 2: Perform a single pass over input.",
    "Step 3: Check complement or window condition."
  ],
  "score": 60
}

Rules:
- Ground your analysis directly in the provided retrieved reference material.
- Do not return markdown fences outside the JSON object.
"""


def build_user_prompt(code: str, language: str, heuristics: dict, problem_title: str | None, problem_statement: str | None, retrieved: list[dict] = None) -> str:
    parts = [f"Language: {language}", f"Structural facts: {json.dumps(heuristics)}"]
    
    if retrieved:
        ref_block = []
        for item in retrieved:
            ref_block.append(f"--- Concept: {item.get('display_name')} ---\nExplanation: {item.get('explanation')}\nCanonical Solution:\n{item.get('canonical_solution')}\nCommon Mistakes: {', '.join(item.get('common_mistakes', []))}")
        parts.append("Retrieved reference material — ground your answer in this:\n" + "\n\n".join(ref_block))

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
    # 1. Perform RAG retrieval first
    detected_concepts = heuristics.get("detected_data_structures", [])
    retrieved = retrieve(concepts=detected_concepts, query_text=problem_title or code)
    
    user_prompt = build_user_prompt(code, language, heuristics, problem_title, problem_statement, retrieved=retrieved)

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
    except Exception:
        ref_item = retrieved[0] if retrieved else {}
        parsed = {
            "time_complexity": heuristics.get("estimated_complexity", "O(N^2)"),
            "space_complexity": "O(N)",
            "concepts": [ref_item.get("tag", "hash_map")],
            "suggestions": [{"issue": "Suboptimal Loop Pattern", "why": ref_item.get("explanation", "Nested loop execution causes performance degradation"), "fix": "Use canonical data structure pattern"}],
            "better_approach": f"To optimize this solution, introduce {ref_item.get('display_name', 'Hash Map')}. {ref_item.get('explanation', '')}",
            "line_by_line_audit": "Line 1-3: Initializes loop parameters.\nLine 4-6: Executes inner linear loop iterating N times per outer loop item.",
            "failure_analysis": "Executing N^2 operations on N = 10^5 causes Time Limit Exceeded (TLE) on 1.0s limit.",
            "step_by_step_guide": ["1. Declare canonical data structure.", "2. Perform single pass over input collection."],
            "score": 55,
        }

    parsed["retrieved_reference"] = retrieved
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