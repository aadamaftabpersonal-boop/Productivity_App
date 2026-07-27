from typing import Dict, Any, Optional
from tree_sitter import Parser, Node
import tree_sitter_language_pack

from app.domains.swe import SWEDomainAnalyzer
from app.domains.registry import get_domain_analyzer


async def analyze_multi_file_project(files: Dict[str, str], domain: str = "cp") -> Dict[str, Any]:
    """Analyzes multi-file software repositories for cross-file architecture issues."""
    combined_code = ""
    file_diagnostics = []

    analyzer = get_domain_analyzer(domain)


    for filename, code in files.items():
        analysis = await analyzer.analyze(code, "python")
        combined_code += f"\n# File: {filename}\n" + code
        file_diagnostics.append({
            "filename": filename,
            "heuristics": analysis["heuristics"],
            "suggestions": analysis["review_data"]["suggestions"],
        })

    # Cross-file specific checks (e.g. fit in dataset.py, split in train.py)
    cross_file_suggestions = []
    if domain.lower() == "ml":
        dataset_code = next((code for fn, code in files.items() if "data" in fn.lower()), "")
        train_code = next((code for fn, code in files.items() if "train" in fn.lower() or "main" in fn.lower()), "")

        if "fit" in dataset_code and "train_test_split" in train_code:
            cross_file_suggestions.append({
                "issue": "Cross-File Data Leakage",
                "why": "Dataset preprocessing script `dataset.py` invokes `.fit()` on global data before `train.py` executes data split.",
                "fix": "Defer preprocessing fit transforms until after dataset is split inside `train.py`.",
            })

    return {
        "domain": domain,
        "file_count": len(files),
        "file_diagnostics": file_diagnostics,
        "cross_file_suggestions": cross_file_suggestions,
        "total_flaws_found": sum(len(f["suggestions"]) for f in file_diagnostics) + len(cross_file_suggestions),
    }
