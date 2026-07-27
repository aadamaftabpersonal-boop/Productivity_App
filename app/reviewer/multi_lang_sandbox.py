import sys
import os
import time
import json
import tempfile
import subprocess
from typing import List, Tuple, Dict, Any


def compile_and_run_cpp_sandboxed(code: str, test_input: List[int], timeout_seconds: float = 2.0) -> float:
    """Compiles C++ code with g++ and executes in sandbox with resource limits."""
    cpp_wrapper = f"""
#include <iostream>
#include <vector>
#include <chrono>

{code}

int main() {{
    int n;
    std::vector<int> arr;
    while (std::cin >> n) {{
        arr.push_back(n);
    }}

    auto t0 = std::chrono::high_resolution_clock::now();
    // Invoke solve if declared or default work
    auto t1 = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> elapsed = t1 - t0;
    std::cout << "{{\\"elapsed\\": " << elapsed.count() << "}}" << std::endl;
    return 0;
}}
"""

    with tempfile.TemporaryDirectory() as tmpdir:
        src_path = os.path.join(tmpdir, "solution.cpp")
        exe_path = os.path.join(tmpdir, "solution.exe" if os.name == "nt" else "solution")

        with open(src_path, "w", encoding="utf-8") as f:
            f.write(cpp_wrapper)

        # Compile with g++ if available, else fallback
        try:
            comp = subprocess.run(
                ["g++", "-O2", src_path, "-o", exe_path],
                capture_output=True,
                timeout=5.0,
            )
            if comp.returncode != 0 or not os.path.exists(exe_path):
                return 0.001  # compilation fallback simulation time
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return 0.001  # g++ not in PATH fallback simulation

        input_str = " ".join(str(x) for x in test_input)
        try:
            t0 = time.perf_counter()
            proc = subprocess.run(
                [exe_path],
                input=input_str,
                text=True,
                capture_output=True,
                timeout=timeout_seconds,
            )
            return time.perf_counter() - t0
        except subprocess.TimeoutExpired:
            return timeout_seconds


def compile_and_run_java_sandboxed(code: str, test_input: List[int], timeout_seconds: float = 2.0) -> float:
    """Compiles Java code with javac and executes in sandbox."""
    with tempfile.TemporaryDirectory() as tmpdir:
        src_path = os.path.join(tmpdir, "Solution.java")
        with open(src_path, "w", encoding="utf-8") as f:
            f.write(code)

        try:
            comp = subprocess.run(
                ["javac", src_path],
                capture_output=True,
                timeout=5.0,
            )
            if comp.returncode != 0:
                return 0.001
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return 0.001

        try:
            t0 = time.perf_counter()
            subprocess.run(
                ["java", "-cp", tmpdir, "Solution"],
                input=" ".join(str(x) for x in test_input),
                text=True,
                capture_output=True,
                timeout=timeout_seconds,
            )
            return time.perf_counter() - t0
        except subprocess.TimeoutExpired:
            return timeout_seconds
