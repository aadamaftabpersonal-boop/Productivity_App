import pytest
from app.reviewer.fuzzer import run_fuzz_suite


def test_fuzzer_runs_boundary_cases():
    valid_code = """
def solve(arr):
    if not arr:
        return 0
    return sum(arr)
"""
    fuzz_res = run_fuzz_suite(valid_code, "python")
    assert fuzz_res["total_cases"] == 5
    assert fuzz_res["passed_cases"] == 5
    assert fuzz_res["failed_cases"] == 0
    assert len(fuzz_res["results"]) == 5
