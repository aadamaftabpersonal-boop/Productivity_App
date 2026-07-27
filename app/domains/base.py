from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class DomainAnalyzer(ABC):
    @property
    @abstractmethod
    def domain_name(self) -> str:
        """Domain identifier e.g. 'cp', 'ml', or 'swe'."""
        pass

    @abstractmethod
    async def analyze(
        self,
        code: str,
        language: str,
        problem_title: Optional[str] = None,
        problem_statement: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Analyzes submission and returns {structural_facts, llm_review, verified_claims}."""
        pass
