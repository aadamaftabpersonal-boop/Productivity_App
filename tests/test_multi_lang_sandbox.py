import pytest
from app.reviewer.multi_lang_sandbox import compile_and_run_cpp_sandboxed, compile_and_run_java_sandboxed


def test_cpp_sandbox_execution_fallback():
    cpp_code = "void solve() { int a = 5; }"
    elapsed = compile_and_run_cpp_sandboxed(cpp_code, [1, 2, 3])
    assert elapsed >= 0.0


def test_java_sandbox_execution_fallback():
    java_code = "public class Solution { public static void main(String[] args) {} }"
    elapsed = compile_and_run_java_sandboxed(java_code, [1, 2, 3])
    assert elapsed >= 0.0
