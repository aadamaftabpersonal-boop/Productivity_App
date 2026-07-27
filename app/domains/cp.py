from typing import Dict, Any, Optional
from app.domains.base import DomainAnalyzer
from app.reviewer.tree_analysis import analyze_structure
from app.reviewer.llm_review import get_review
from app.reviewer.complexity_sandbox import measure_empirical_complexity, cross_check_complexity
from app.weakness.problem_bank import compare_against_reference_optimal


class CPDomainAnalyzer(DomainAnalyzer):
    @property
    def domain_name(self) -> str:
        return "cp"

    async def analyze(
        self,
        code: str,
        language: str,
        problem_title: Optional[str] = None,
        problem_statement: Optional[str] = None,
    ) -> Dict[str, Any]:
        heuristics = analyze_structure(code, language)

        review_data = await get_review(
            code=code,
            language=language,
            heuristics=heuristics,
            problem_title=problem_title,
            problem_statement=problem_statement,
        )

        empirical_fit, _ = measure_empirical_complexity(code, language)
        has_disagreement, warning_msg = cross_check_complexity(
            review_data.get("time_complexity"), empirical_fit
        )

        ref_opt = compare_against_reference_optimal(problem_title or "", empirical_fit)

        return {
            "heuristics": heuristics,
            "review_data": review_data,
            "measured_complexity": empirical_fit,
            "complexity_disagreement": has_disagreement,
            "complexity_warning": warning_msg,
            "reference_optimal": ref_opt,
        }
