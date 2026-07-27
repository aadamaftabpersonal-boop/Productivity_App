import os
import asyncio
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database import AsyncSessionLocal
from app.models import CodeSubmission, ReviewResult
from app.reviewer.llm_review import get_review
from app.reviewer.complexity_sandbox import measure_empirical_complexity, cross_check_complexity


async def run_review_pipeline(submission_id: str) -> Optional[dict]:
    """Core review task pipeline executed asynchronously in background job."""
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(CodeSubmission).where(CodeSubmission.id == submission_id)
        )
        submission = result.scalar_one_or_none()
        if not submission:
            return None

        from app.domains.registry import get_domain_analyzer

        analyzer = get_domain_analyzer(submission.domain or "cp")

        try:
            analysis_output = await analyzer.analyze(
                code=submission.code,
                language=submission.language,
                problem_title=submission.problem_title,
                problem_statement=submission.problem_statement,
            )
            heuristics = analysis_output["heuristics"]
            review_data = analysis_output["review_data"]
            empirical_fit = analysis_output["measured_complexity"]
            has_disagreement = analysis_output["complexity_disagreement"]
            warning_msg = analysis_output["complexity_warning"]
        except Exception as e:
            heuristics = {}
            review_data = {
                "time_complexity": "O(n)",
                "space_complexity": "O(1)",
                "concepts": [],
                "suggestions": [],
                "better_approach": f"Review generation failed: {str(e)}",
                "score": 0,
            }
            empirical_fit = "O(n)"
            has_disagreement = False
            warning_msg = None


        review = ReviewResult(
            submission_id=submission.id,
            time_complexity=review_data.get("time_complexity"),
            space_complexity=review_data.get("space_complexity"),
            measured_complexity=empirical_fit,
            complexity_disagreement=has_disagreement,
            complexity_warning=warning_msg,
            concepts=review_data.get("concepts", []),
            suggestions=review_data.get("suggestions", []),
            better_approach=review_data.get("better_approach"),
            score=review_data.get("score"),
            raw_heuristics=heuristics,
        )
        db.add(review)
        await db.commit()

        try:
            from app.weakness.service import process_review_for_weaknesses
            await process_review_for_weaknesses(db, submission.id, submission.user_id)
        except Exception as e:
            print(f"Background weakness tracking failed: {str(e)}")

        return review_data


# arq worker definition
async def process_submission_job(ctx: Dict[Any, Any], submission_id: str):
    return await run_review_pipeline(submission_id)


class WorkerSettings:
    functions = [process_submission_job]
    redis_settings = None  # Uses default Redis connection if available
