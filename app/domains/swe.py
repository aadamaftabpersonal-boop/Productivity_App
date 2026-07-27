import re
from typing import Dict, Any, Optional
from tree_sitter import Parser, Node
import tree_sitter_language_pack

from app.domains.base import DomainAnalyzer


class SWEDomainAnalyzer(DomainAnalyzer):
    @property
    def domain_name(self) -> str:
        return "swe"

    async def analyze(
        self,
        code: str,
        language: str = "python",
        problem_title: Optional[str] = None,
        problem_statement: Optional[str] = None,
    ) -> Dict[str, Any]:
        """SWE software maintainability & longitudinal weakness tracking analyzer."""
        lang_pack_name = "python" if language.lower() in ("python", "py") else "cpp"
        language_pack = tree_sitter_language_pack.get_language(lang_pack_name)
        parser = Parser(language_pack)
        tree = parser.parse(bytes(code, "utf8"))
        root = tree.root_node

        detected_flaws = []
        suggestions = []

        # 1. Bare exception / Error swallowing check
        if re.search(r"except\s*:\s*pass", code) or re.search(r"except\s+Exception\s*:\s*pass", code):
            detected_flaws.append("error_swallowing")
            suggestions.append({
                "issue": "Silent Error Swallowing",
                "why": "Bare `except: pass` catches and swallows all exceptions without logging or re-raising, obscuring production runtime failures.",
                "fix": "Catch specific exception types, log tracebacks, or re-raise appropriate domain errors.",
            })

        # 2. Resource leak without context manager
        if ("open(" in code and "with " not in code) or ("connect(" in code and "with " not in code):
            detected_flaws.append("resource_leak")
            suggestions.append({
                "issue": "Resource Leak Risk",
                "why": "File or socket connection opened without a context manager (`with` block), risking unclosed descriptors on exception.",
                "fix": "Wrap file/socket acquisitions inside `with open(...)` or `with connection:` managers.",
            })

        # 3. Mutable default arguments
        if re.search(r"def\s+\w+\s*\([^)]*=\s*(\[\]|\{\})", code):
            detected_flaws.append("mutable_default_arg")
            suggestions.append({
                "issue": "Mutable Default Argument",
                "why": "Default mutable arguments (`list` or `dict`) persist mutations across function invocations globally.",
                "fix": "Default to `None` and initialize the container inside the function body.",
            })

        score = max(0, 100 - len(suggestions) * 20)

        return {
            "heuristics": {
                "detected_swe_flaws": detected_flaws,
                "node_count": root.descendant_count,
            },
            "review_data": {
                "time_complexity": "O(N)",
                "space_complexity": "O(N)",
                "concepts": ["maintainability", "resource_management", "error_handling"],
                "suggestions": suggestions,
                "better_approach": (
                    "SWE Maintainability Review: Avoid silent exception swallowing, enforce deterministic resource context managers, "
                    "and remove mutable default parameters to prevent cross-call state mutation."
                ),
                "score": score,
            },
            "measured_complexity": "O(N)",
            "complexity_disagreement": False,
            "complexity_warning": None,
        }
