from app.reviewer.preflight import check_preflight


def test_integer_overflow_true_positive_cpp():
    heuristics = {"has_recursion": False}
    code = "int main() { int n = 100000; int val = n * n; }"
    warnings = check_preflight(heuristics, "cpp", code)
    assert any(w["type"] == "integer_overflow_risk" for w in warnings)


def test_integer_overflow_suppressed_in_python():
    """Python arbitrary precision prevents 32-bit int overflow false positives."""
    heuristics = {"has_recursion": False}
    code = "def solve(n):\n    val = n * n\n    return val"
    warnings = check_preflight(heuristics, "python", code)
    assert not any(w["type"] == "integer_overflow_risk" for w in warnings)


def test_fast_io_endl_warning_cpp():
    heuristics = {"has_recursion": False}
    code = '#include <iostream>\nint main() { std::cout << "test" << std::endl; }'
    warnings = check_preflight(heuristics, "cpp", code)
    assert any(w["type"] == "fast_io_endl" for w in warnings)


def test_unbounded_recursion_warning():
    heuristics = {"has_recursion": True}
    code = "def dfs(node):\n    for nxt in node.neighbors:\n        dfs(nxt)"
    warnings = check_preflight(heuristics, "python", code)
    assert any(w["type"] == "unbounded_recursion_risk" for w in warnings)


def test_recursion_with_base_case_passes():
    heuristics = {"has_recursion": True}
    code = "def dfs(node):\n    if not node: return\n    for nxt in node.neighbors:\n        dfs(nxt)"
    warnings = check_preflight(heuristics, "python", code)
    assert not any(w["type"] == "unbounded_recursion_risk" for w in warnings)
