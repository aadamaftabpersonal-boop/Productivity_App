import pytest
from app.reviewer.complexity_sandbox import (
    fit_growth_curve,
    run_python_sandboxed,
    measure_empirical_complexity,
    cross_check_complexity,
)


def test_known_quadratic_solution_measured_as_n2():
    # Deliberate quadratic O(n^2) nested loop Python code
    quadratic_code = """
def solve(arr):
    total = 0
    n = len(arr)
    for i in range(n):
        for j in range(n):
            total += arr[i] ^ arr[j]
    return total
"""
    fit_label, timing_map = measure_empirical_complexity(quadratic_code, "python")
    assert fit_label == "O(n^2)"
    assert len(timing_map) == 5


def test_disagreement_with_wrong_llm_claim_surfaces_both():
    # Known quadratic code empirical fit = O(n^2)
    fit_label = "O(n^2)"
    wrong_llm_claim = "O(n log n)"

    has_disagreement, warning_msg = cross_check_complexity(wrong_llm_claim, fit_label)

    assert has_disagreement is True
    assert warning_msg is not None
    assert "LLM claimed O(n log n)" in warning_msg
    assert "closer to O(n^2)" in warning_msg
    assert "treat the LLM claim with caution" in warning_msg
