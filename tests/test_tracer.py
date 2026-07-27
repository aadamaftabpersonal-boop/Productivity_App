from app.reviewer.tracer import trace_python_execution, MAX_TRACE_STEPS


def test_tracer_captures_valid_line_and_variable_snapshots():
    code = """def solve(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        diff = target - num
        if diff in seen:
            return [seen[diff], i]
        seen[num] = i
    return []
"""
    steps = trace_python_execution(code)
    assert len(steps) >= 1
    assert "line_no" in steps[0]
    assert "variables" in steps[0]


def test_tracer_enforces_200_step_cap():
    """Asserts long loops are capped at MAX_TRACE_STEPS (200)."""
    code = """def infinite_loop():
    i = 0
    while i < 1000:
        i += 1
solve = infinite_loop
"""
    steps = trace_python_execution(code)
    assert len(steps) <= MAX_TRACE_STEPS


def test_tracer_sandbox_timeout_preserved():
    """Asserts infinite loops terminate within timeout limit without hanging."""
    code = """def hard_infinite():
    while True:
        pass
solve = hard_infinite
"""
    steps = trace_python_execution(code)
    assert len(steps) >= 1
    assert "Timeout" in steps[0].get("code_line", "") or "error" in steps[0].get("variables", {})
