import pytest
from app.domains.swe import SWEDomainAnalyzer


@pytest.mark.asyncio
async def test_swe_analyzer_catches_error_swallowing_and_resource_leaks():
    analyzer = SWEDomainAnalyzer()
    bad_code = """
def load_config(filepath, options={}):
    try:
        f = open(filepath, 'r')
        data = f.read()
    except Exception:
        pass
    return data
"""
    res = await analyzer.analyze(bad_code, "python")
    flaws = res["heuristics"]["detected_swe_flaws"]
    assert "error_swallowing" in flaws
    assert "resource_leak" in flaws
    assert "mutable_default_arg" in flaws
    assert len(res["review_data"]["suggestions"]) == 3
