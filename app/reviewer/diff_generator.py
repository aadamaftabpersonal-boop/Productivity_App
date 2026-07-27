import difflib
from typing import Optional
from app.reviewer.llm_review import client


DIFF_PROMPT_TEMPLATE = """You are a senior code reviewer. Convert the following student solution into an optimal, production-ready solution in {language}.
Return ONLY the complete optimal code block, with no explanations, markdown formatting, or preamble.

Original Code:
```{language}
{code}
```
"""


async def generate_optimal_code_diff(code: str, language: str = "python") -> Optional[str]:
    """Generates unified git diff patch refactoring user code into optimal complexity."""
    try:
        completion = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "user", "content": DIFF_PROMPT_TEMPLATE.format(code=code, language=language)},
            ],
            temperature=0.2,
            max_tokens=1000,
        )
        optimal_code = completion.choices[0].message.content.strip()

        # Clean markdown code fences if present
        if optimal_code.startswith("```"):
            lines = optimal_code.splitlines()
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].startswith("```"):
                lines = lines[:-1]
            optimal_code = "\n".join(lines)

        diff = difflib.unified_diff(
            code.splitlines(keepends=True),
            optimal_code.splitlines(keepends=True),
            fromfile="original.py",
            tofile="optimal_refactored.py",
        )
        return "".join(diff)
    except Exception as e:
        return f"--- original.py\n+++ optimal_refactored.py\n@@ -1 +1 @@\n# Refactoring diff unavailable: {str(e)}"
