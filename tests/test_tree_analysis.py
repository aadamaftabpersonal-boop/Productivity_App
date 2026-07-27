import pytest
from app.reviewer.tree_analysis import analyze_structure

def test_decoy_variable_does_not_trigger_hash_map():
    # Decoy variable names mapValue / dict_data should NOT trigger hash_map hint
    py_decoy = """
def process_data(items):
    mapValue = 5
    dict_data = 10
    return mapValue + dict_data
"""
    res = analyze_structure(py_decoy, "python")
    assert "hash_map" not in res["data_structure_hints"]

    cpp_decoy = """
int solve(int n) {
    int mapValue = 5;
    int dict_val = 10;
    return mapValue + dict_val;
}
"""
    res_cpp = analyze_structure(cpp_decoy, "cpp")
    assert "hash_map" not in res_cpp["data_structure_hints"]

    java_decoy = """
public class Solution {
    public int solve(int n) {
        int mapValue = 5;
        return mapValue;
    }
}
"""
    res_java = analyze_structure(java_decoy, "java")
    assert "hash_map" not in res_java["data_structure_hints"]


def test_real_data_structure_declarations_detected():
    py_code = """
from collections import defaultdict

def solve(arr):
    counts = defaultdict(int)
    seen = set()
    return counts, seen
"""
    res_py = analyze_structure(py_code, "python")
    assert "hash_map" in res_py["data_structure_hints"]
    assert "set" in res_py["data_structure_hints"]

    cpp_code = """
#include <unordered_map>
#include <vector>

void solve() {
    std::unordered_map<int, int> mp;
    std::vector<int> vec;
}
"""
    res_cpp = analyze_structure(cpp_code, "cpp")
    assert "hash_map" in res_cpp["data_structure_hints"]
    assert "vector_array_list" in res_cpp["data_structure_hints"]

    java_code = """
import java.util.*;

public class Solution {
    public void solve() {
        Map<Integer, Integer> map = new HashMap<>();
        List<Integer> list = new ArrayList<>();
    }
}
"""
    res_java = analyze_structure(java_code, "java")
    assert "hash_map" in res_java["data_structure_hints"]
    assert "vector_array_list" in res_java["data_structure_hints"]


def test_decoy_function_substring_does_not_trigger_recursion():
    # Function solve_helper containing 'solve' as substring inside body must NOT trigger recursion on solve
    py_decoy_rec = """
def solve_helper(n):
    return n * 2

def solve(n):
    res = solve_helper(n)
    return res
"""
    res_py = analyze_structure(py_decoy_rec, "python")
    assert res_py["likely_recursive"] is False

    cpp_decoy_rec = """
int solve_helper(int n) {
    return n * 2;
}

int solve(int n) {
    return solve_helper(n);
}
"""
    res_cpp = analyze_structure(cpp_decoy_rec, "cpp")
    assert res_cpp["likely_recursive"] is False


def test_real_recursion_detected():
    py_rec = """
def fib(n):
    if n <= 1:
        return n
    return fib(n - 1) + fib(n - 2)
"""
    res_py = analyze_structure(py_rec, "python")
    assert res_py["likely_recursive"] is True

    cpp_rec = """
int fib(int n) {
    if (n <= 1) return n;
    return fib(n - 1) + fib(n - 2);
}
"""
    res_cpp = analyze_structure(cpp_rec, "cpp")
    assert res_cpp["likely_recursive"] is True
