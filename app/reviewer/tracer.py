"""Sandboxed Dry-Run Python Execution Tracer.

Uses sys.settrace in a sandboxed subprocess to record line-by-line variable state snapshots.
Enforces a hard 200-step cap and a 2.0s execution timeout.
"""
import sys
import multiprocessing
from typing import List, Dict, Any

MAX_TRACE_STEPS = 200
TIMEOUT_SECONDS = 2.0


def _worker_trace(code: str, queue: multiprocessing.Queue):
    steps = []
    lines = code.splitlines()

    def trace_func(frame, event, arg):
        if len(steps) >= MAX_TRACE_STEPS:
            return None  # Stop tracing

        if event == "line":
            line_no = frame.f_lineno
            # Extract safe serializable locals (primitive types & small collections)
            local_vars = {}
            for k, v in frame.f_locals.items():
                if k.startswith("__") or callable(v):
                    continue
                try:
                    str_val = str(v)
                    if len(str_val) > 100:
                        str_val = str_val[:97] + "..."
                    local_vars[k] = str_val
                except Exception:
                    pass

            code_line = lines[line_no - 1] if 0 <= line_no - 1 < len(lines) else ""
            steps.append({
                "step": len(steps) + 1,
                "line_no": line_no,
                "code_line": code_line.strip(),
                "variables": local_vars,
            })
        return trace_func

    try:
        namespace = {}
        sys.settrace(trace_func)
        exec(code, namespace)
        # If solve() function is defined, invoke solve() with sample inputs
        if "solve" in namespace and callable(namespace["solve"]):
            try:
                # Try sample invocations
                sig_count = namespace["solve"].__code__.co_argcount
                if sig_count == 0:
                    namespace["solve"]()
                elif sig_count == 1:
                    namespace["solve"]([2, 7, 11, 15])
                elif sig_count == 2:
                    namespace["solve"]([2, 7, 11, 15], 9)
            except Exception:
                pass
        sys.settrace(None)
    except Exception as e:
        sys.settrace(None)
        steps.append({
            "step": len(steps) + 1,
            "line_no": 1,
            "code_line": f"Execution Error: {type(e).__name__}",
            "variables": {"error": str(e)},
        })

    queue.put(steps[:MAX_TRACE_STEPS])


def trace_python_execution(code: str) -> List[Dict[str, Any]]:
    """Runs Python code in a sandboxed subprocess and returns line/variable trace up to 200 steps."""
    queue = multiprocessing.Queue()
    proc = multiprocessing.Process(target=_worker_trace, args=(code, queue))
    proc.start()
    proc.join(TIMEOUT_SECONDS)

    if proc.is_alive():
        proc.terminate()
        proc.join()
        return [{
            "step": 1,
            "line_no": 1,
            "code_line": "Execution Timeout (>2.0s)",
            "variables": {"error": "Trace terminated after 2.0s timeout limit."}
        }]

    if not queue.empty():
        return queue.get()

    return [{
        "step": 1,
        "line_no": 1,
        "code_line": "Trace Completed",
        "variables": {"status": "No lines traced."}
    }]
