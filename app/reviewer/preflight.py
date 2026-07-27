"""Pre-flight Anti-Bug Checklist module.

Performs instant static analysis over Tree-sitter heuristics and source code text to flag:
1. Integer overflow risks in C++/Java (32-bit int multiplication without 64-bit cast)
2. Fast I/O bottlenecks in C++ (std::endl flush TLE risk, missing cin.tie(NULL))
3. Unbounded recursion risks (recursion flagged without visible base-case return)
"""
import re
from typing import List, Dict, Any


def check_preflight(heuristics: Dict[str, Any], language: str, code: str) -> List[Dict[str, Any]]:
    """Returns user-facing preflight warnings based on structural facts and source code."""
    warnings = []
    lang = language.lower()

    # 1. Integer Overflow Risk (C++ / Java only - Python has arbitrary-precision ints)
    if lang in ("cpp", "c++", "java"):
        # Check for 32-bit int multiplication producing potentially large values (e.g. n * n or 100000 * 100000)
        has_int_mult = re.search(r'\b(int|int32_t)\s+\w+\s*=\s*\w+\s*\*\s*\w+', code) or re.search(r'\b\w+\s*\*\s*\w+\b', code)
        has_64bit_cast = "long long" in code or "int64_t" in code or "(long)" in code or "BigInteger" in code
        
        if has_int_mult and not has_64bit_cast and ("1000" in code or "10^" in code or "N *" in code or "n *" in code or "n*n" in code or "nums.size()" in code):
            warnings.append({
                "type": "integer_overflow_risk",
                "severity": "warning",
                "title": "Integer Overflow Risk (32-bit int multiplication)",
                "message": "Multiplication between 32-bit signed integers can overflow 2^31-1 (~2*10^9) in C++/Java. Cast operands to `long long` or `int64_t`."
            })

    # 2. Fast I/O Warning (C++ only)
    if lang in ("cpp", "c++"):
        if "std::endl" in code or "endl;" in code:
            warnings.append({
                "type": "fast_io_endl",
                "severity": "warning",
                "title": "Fast I/O Bottleneck (`std::endl` Flushes Output Buffer)",
                "message": "Using `std::endl` forces an expensive I/O buffer flush on every line, risking TLE on 10^5 operations. Replace with `'\\n'`."
            })
        if ("cin >>" in code or "cout <<" in code) and not ("cin.tie" in code or "sync_with_stdio" in code):
            warnings.append({
                "type": "fast_io_missing_sync",
                "severity": "warning",
                "title": "Missing Fast I/O Sync (`ios::sync_with_stdio(false)`)",
                "message": "C++ I/O stream synchronization with C stdio adds ~300ms overhead. Add `ios::sync_with_stdio(false); cin.tie(NULL);` at main entry."
            })

    # 3. Unbounded Recursion Risk (All Languages)
    if heuristics.get("has_recursion", False):
        has_base_case = re.search(r'\bif\b.*\breturn\b', code, re.DOTALL) or "base" in code.lower()
        if not has_base_case:
            warnings.append({
                "type": "unbounded_recursion_risk",
                "severity": "error",
                "title": "Unbounded Recursion Risk (Missing Base Case Return)",
                "message": "Recursion detected by AST parser without a clear `if (...) return` base-case guard before self-invocations. High StackOverflowError / segmentation fault risk."
            })

    return warnings
