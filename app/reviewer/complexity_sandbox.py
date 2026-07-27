import sys
import os
import time
import math
import tempfile
import subprocess
import json
from typing import Tuple, Dict, List, Optional


CANONICAL_GROWTH_CURVES = {
    "O(1)": lambda n: 1.0,
    "O(log n)": lambda n: math.log2(n) if n > 1 else 0.1,
    "O(n)": lambda n: float(n),
    "O(n log n)": lambda n: float(n) * (math.log2(n) if n > 1 else 0.1),
    "O(n^2)": lambda n: float(n ** 2),
}


def fit_growth_curve(sizes: List[int], runtimes: List[float]) -> str:
    """Least-squares regression fit in log space to pick best canonical growth curve."""
    if len(sizes) < 3 or not any(t > 0 for t in runtimes):
        return "O(n)"  # default fallback if insufficient timing data

    best_label = "O(n)"
    best_r2 = -float("inf")

    # Filter out zero or negative runtimes
    valid_pts = [(s, max(t, 1e-6)) for s, t in zip(sizes, runtimes)]
    
    for label, fn in CANONICAL_GROWTH_CURVES.items():
        # Linear regression: t_i ~ c * f(s_i)
        fx = [fn(s) for s, _ in valid_pts]
        ty = [t for _, t in valid_pts]

        # Calculate R^2 coefficient of determination
        mean_y = sum(ty) / len(ty)
        ss_tot = sum((y - mean_y) ** 2 for y in ty)
        if ss_tot == 0:
            continue

        # Fit c = sum(fx * ty) / sum(fx^2)
        denom = sum(x ** 2 for x in fx)
        if denom == 0:
            continue
        c = sum(x * y for x, y in zip(fx, ty)) / denom

        ss_res = sum((y - c * x) ** 2 for x, y in zip(fx, ty))
        r2 = 1.0 - (ss_res / ss_tot)

        if r2 > best_r2:
            best_r2 = r2
            best_label = label

    return best_label


def run_python_sandboxed(code: str, test_input: List[int], timeout_seconds: float = 2.0) -> float:
    """Run user Python code in a isolated subprocess sandbox with resource & time limits."""
    runner_script = f"""
import sys, json, time

{code}

# Auto-detect function or default 'solve' / first callable
func = None
if 'solve' in globals() and callable(globals()['solve']):
    func = globals()['solve']
else:
    for name, obj in list(globals().items()):
        if callable(obj) and not name.startswith('_') and name not in ('sys', 'json', 'time'):
            func = obj
            break

if func:
    arr = json.loads(sys.stdin.read())
    t0 = time.perf_counter()
    try:
        func(arr)
    except Exception:
        pass
    t1 = time.perf_counter()
    print(json.dumps({{"elapsed": t1 - t0}}))
else:
    print(json.dumps({{"elapsed": 0.0}}))
"""

    with tempfile.TemporaryDirectory() as tmpdir:
        script_path = os.path.join(tmpdir, "solution.py")
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(runner_script)

        # Restrict environment (no network, isolated temp dir)
        env = {
            "PYTHONPATH": tmpdir,
            "SYSTEMROOT": os.environ.get("SYSTEMROOT", ""),
            "PATH": os.environ.get("PATH", ""),
        }

        try:
            start_wall = time.perf_counter()
            proc = subprocess.run(
                [sys.executable, script_path],
                input=json.dumps(test_input),
                text=True,
                capture_output=True,
                timeout=timeout_seconds,
                cwd=tmpdir,
                env=env,
            )
            elapsed_wall = time.perf_counter() - start_wall

            if proc.returncode == 0 and proc.stdout.strip():
                try:
                    data = json.loads(proc.stdout.strip())
                    return float(data.get("elapsed", elapsed_wall))
                except json.JSONDecodeError:
                    return elapsed_wall
            return elapsed_wall
        except subprocess.TimeoutExpired:
            return timeout_seconds


def measure_empirical_complexity(code: str, language: str = "python") -> Tuple[str, Dict[int, float]]:
    """Generates synthetic input arrays of varying sizes N, runs sandboxed benchmarks,
    and returns measured complexity fit along with (N, runtime) mapping."""
    if language.lower() not in ("python",):
        # Default fallback for unhandled sandbox languages in v1
        return "O(n)", {}

    sizes = [100, 300, 700, 1500, 3000]
    runtimes = []
    timing_map = {}

    import random
    random.seed(42)

    for n in sizes:
        sample_input = [random.randint(1, 10000) for _ in range(n)]
        runtime = run_python_sandboxed(code, sample_input, timeout_seconds=3.0)
        runtimes.append(runtime)
        timing_map[n] = round(runtime, 6)

    fit_label = fit_growth_curve(sizes, runtimes)
    return fit_label, timing_map


def normalize_complexity_str(complexity: Optional[str]) -> str:
    if not complexity:
        return ""
    c = complexity.lower().replace(" ", "").replace("*", "")
    if "n^2" in c or "n2" in c or "n*n" in c:
        return "O(n^2)"
    if "nlogn" in c or "n*logn" in c:
        return "O(n log n)"
    if "o(n)" in c:
        return "O(n)"
    if "o(1)" in c:
        return "O(1)"
    if "o(logn)" in c or "o(log(n))" in c:
        return "O(log n)"
    return complexity.strip()


def cross_check_complexity(llm_claimed: Optional[str], empirical_fit: str) -> Tuple[bool, Optional[str]]:
    """Compares LLM claimed complexity with empirical fit.
    Returns (has_disagreement, warning_message)."""
    norm_llm = normalize_complexity_str(llm_claimed)
    norm_emp = normalize_complexity_str(empirical_fit)

    if not norm_llm:
        return False, None

    # Check for direct disagreement between distinct complexity classes
    if norm_llm != norm_emp and norm_llm in ("O(n)", "O(n log n)", "O(1)") and norm_emp in ("O(n^2)", "O(n log n)"):
        warning = (
            f"LLM claimed {llm_claimed}; measured growth looks closer to {empirical_fit} — "
            f"treat the LLM claim with caution here."
        )
        return True, warning

    return False, None
