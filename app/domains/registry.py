from typing import Dict
from app.domains.base import DomainAnalyzer
from app.domains.cp import CPDomainAnalyzer

_ANALYZERS: Dict[str, DomainAnalyzer] = {
    "cp": CPDomainAnalyzer(),
}


def register_domain_analyzer(analyzer: DomainAnalyzer):
    _ANALYZERS[analyzer.domain_name] = analyzer


def get_domain_analyzer(domain: str) -> DomainAnalyzer:
    analyzer = _ANALYZERS.get(domain.lower())
    if not analyzer:
        # Fallback to CP analyzer
        return _ANALYZERS["cp"]
    return analyzer
