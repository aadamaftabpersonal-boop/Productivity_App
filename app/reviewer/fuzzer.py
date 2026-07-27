import sys
import os
import json
from typing import Dict, List, Any
from app.reviewer.complexity_sandbox import run_python_sandboxed


CORNER_CASE_SUITES = [
    {"name": "Empty Input", "input": []},
    {"name": "Single Element", "input": [0]},
    {"name": "Extreme Boundary Values", "input": [-2147483648, 0, 2147483647]},
    {"name": "All Identical Elements", "input": [42, 42, 42, 42, 42]},
    {"name": "Reverse Sorted Input", "input": [100, 80, 60, 40, 20, 0]},
]


def run_fuzz_suite(code: str, language: str = "python") -> Dict[str, Any]:
    """Empirically stress-tests submitted code against boundary inputs in the sandbox."""
    if language.lower() not in ("python",):
        return {"total_cases": 0, "passed_cases": 0, "failed_cases": 0, "results": []}

    results = []
    passed = 0
    failed = 0

    for case in CORNER_CASE_SUITES:
        case_name = case["name"]
        test_input = case["input"]

        elapsed = run_python_sandboxed(code, test_input, timeout_seconds=1.5)

        if elapsed >= 1.4:
            status = "TIMEOUT"
            failed += 1
            error_detail = "Execution timed out on boundary input"
        else:
            status = "PASS"
            passed += 1
            error_detail = None

        results.append({
            "case_name": case_name,
            "status": status,
            "elapsed_seconds": round(elapsed, 4),
            "error_detail": error_detail,
        })

    return {
        "total_cases": len(CORNER_CASE_SUITES),
        "passed_cases": passed,
        "failed_cases": failed,
        "results": results,
    }
