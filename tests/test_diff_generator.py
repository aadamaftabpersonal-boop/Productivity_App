import pytest
from app.reviewer.diff_generator import generate_optimal_code_diff


@pytest.mark.asyncio
async def test_diff_generator_returns_unified_diff(monkeypatch):
    async def _fake_groq_call(*args, **kwargs):
        class Choice:
            class Message:
                content = "def solve(arr):\n    return sum(arr)"
            message = Message()
        class Completion:
            choices = [Choice()]
        return Completion()

    monkeypatch.setattr(
        "app.reviewer.diff_generator.client.chat.completions.create",
        _fake_groq_call,
    )

    code = "def solve(arr):\n    s = 0\n    for x in arr:\n        s += x\n    return s"
    diff_text = await generate_optimal_code_diff(code, "python")
    assert "--- original.py" in diff_text
    assert "+++ optimal_refactored.py" in diff_text
    assert "def solve(arr):" in diff_text
