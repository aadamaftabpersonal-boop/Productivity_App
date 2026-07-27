import re
from typing import Dict, Any, Optional, List
from tree_sitter import Parser, Node
import tree_sitter_language_pack

from app.domains.base import DomainAnalyzer


class MLDomainAnalyzer(DomainAnalyzer):
    @property
    def domain_name(self) -> str:
        return "ml"

    async def analyze(
        self,
        code: str,
        language: str = "python",
        problem_title: Optional[str] = None,
        problem_statement: Optional[str] = None,
    ) -> Dict[str, Any]:
        """ML code diagnostic analyzer for statistical, leakage, shape, and metric bugs."""
        language_pack = tree_sitter_language_pack.get_language("python")
        parser = Parser(language_pack)
        tree = parser.parse(bytes(code, "utf8"))
        root = tree.root_node

        detected_bugs = []
        suggestions = []

        # 1. Train/Test Contamination Check
        contamination_bug = self._check_train_test_contamination(root, code)
        if contamination_bug:
            detected_bugs.append("train_test_contamination")
            suggestions.append({
                "issue": "Train/Test Data Leakage",
                "why": contamination_bug["why"],
                "fix": contamination_bug["fix"],
            })

        # 2. Non-Reproducibility Check
        reproducibility_bug = self._check_reproducibility(root, code)
        if reproducibility_bug:
            detected_bugs.append("non_reproducible_seed")
            suggestions.append({
                "issue": "Missing Deterministic Seed",
                "why": reproducibility_bug["why"],
                "fix": reproducibility_bug["fix"],
            })

        # 3. Silent Shape Broadcasting Mismatch
        shape_bug = self._check_broadcasting_mismatch(root, code)
        if shape_bug:
            detected_bugs.append("silent_shape_broadcasting")
            suggestions.append({
                "issue": "Silent Tensor Broadcasting Mismatch",
                "why": shape_bug["why"],
                "fix": shape_bug["fix"],
            })

        # 4. Metric Misuse / Train-set Metric as Validation
        metric_bug = self._check_metric_misuse(root, code)
        if metric_bug:
            detected_bugs.append("metric_misuse")
            suggestions.append({
                "issue": "Metric Misuse on Train Data",
                "why": metric_bug["why"],
                "fix": metric_bug["fix"],
            })

        score = max(0, 100 - len(suggestions) * 25)

        return {
            "heuristics": {
                "detected_ml_bugs": detected_bugs,
                "node_count": root.descendant_count,
            },
            "review_data": {
                "time_complexity": "O(N)",
                "space_complexity": "O(N)",
                "concepts": ["ml_data_pipeline", "leakage_prevention", "reproducibility"],
                "suggestions": suggestions,
                "better_approach": (
                    "ML pipeline review: Ensure split occurs before preprocessing fit step, "
                    "explicitly set random seeds for numpy/torch, verify tensor shapes match (N, 1) vs (N,), "
                    "and evaluate precision/recall/F1 alongside validation metrics."
                ),
                "score": score,
            },
            "measured_complexity": "O(N)",
            "complexity_disagreement": False,
            "complexity_warning": None,
        }

    def _check_train_test_contamination(self, root: Node, code: str) -> Optional[dict]:
        """Detects if fit/fit_transform on scaler/vectorizer appears before train_test_split in AST statement order."""
        fit_byte = None
        split_byte = None

        def walk(n: Node):
            nonlocal fit_byte, split_byte
            if n.type == "call":
                fn_child = n.child_by_field_name("function")
                if fn_child:
                    call_text = code[fn_child.start_byte:fn_child.end_byte]
                    if any(m in call_text for m in ("fit_transform", "fit")) and not fit_byte:
                        fit_byte = n.start_byte
                    if "train_test_split" in call_text and not split_byte:
                        split_byte = n.start_byte
            for c in n.children:
                walk(c)

        walk(root)

        if fit_byte is not None and split_byte is not None and fit_byte < split_byte:
            return {
                "why": "Preprocessor `.fit()` or `.fit_transform()` was invoked on the entire dataset prior to `train_test_split()`, leaking test statistics into training.",
                "fix": "Perform `train_test_split()` first, then call `.fit_transform()` only on `X_train`, and `.transform()` on `X_test`.",
            }
        return None

    def _check_reproducibility(self, root: Node, code: str) -> Optional[dict]:
        """Detects use of random data loaders/splits without seed initialization."""
        code_lower = code.lower()
        has_stochastic = any(k in code_lower for k in ("train_test_split", "dataloader", "random_state", "torch", "np.random"))
        has_seed = any(k in code_lower for k in ("seed(", "manual_seed", "random_state="))

        if has_stochastic and not has_seed:
            return {
                "why": "Random data processing or model initialization executed without setting random seeds across numpy/torch/random.",
                "fix": "Set explicit seeds e.g. `np.random.seed(42)`, `torch.manual_seed(42)`, and pass `random_state=42` to data splits.",
            }
        return None

    def _check_broadcasting_mismatch(self, root: Node, code: str) -> Optional[dict]:
        """Detects 1D vs 2D binary subtraction/addition broadcasting pitfalls e.g. `y_pred - y` where shapes differ."""
        if re.search(r"(\w+)\s*[-+]\s*(\w+)", code):
            if re.search(r"reshape\(-1,\s*1\)", code) and re.search(r"-\s*\w+", code) and not re.search(r"\.squeeze\(\)", code):
                return {
                    "why": "Possible 1D vector `(N,)` and 2D column matrix `(N, 1)` binary operation causing unintended 2D outer product broadcasting.",
                    "fix": "Explicitly match array/tensor shapes using `.squeeze()` or `.reshape(-1)` before arithmetic operations.",
                }
        return None

    def _check_metric_misuse(self, root: Node, code: str) -> Optional[dict]:
        """Detects evaluating metrics on training dataset instead of validation set."""
        if re.search(r"accuracy_score\(\s*y_train\s*,", code) or re.search(r"score\(\s*X_train\s*,\s*y_train\s*\)", code):
            return {
                "why": "Evaluation metric is being reported strictly on `X_train` / `y_train`, measuring training memorization rather than generalization error.",
                "fix": "Evaluate and surface metrics on `X_val` / `y_val` or `X_test` / `y_test` validation sets.",
            }
        return None
