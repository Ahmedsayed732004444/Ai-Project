"""
Job-matching service.
"""

import logging
from app.schemas.matching_schema import JobInput, MatchJobsResponse, MatchResult

logger = logging.getLogger(__name__)


def _normalise(skills: list[str]) -> set[str]:
    """Lower-case + strip whitespace."""
    return {s.strip().lower() for s in skills if s.strip()}


def compute_matches(user_skills: list[str], jobs: list[JobInput]) -> MatchJobsResponse:
    """Run the full match pipeline and return a sorted response."""
    user_set = _normalise(user_skills)
    results: list[MatchResult] = []

    for job in jobs:
        job_set = _normalise(job.skills)

        if not job_set:
            match_pct = 0.0
            matched = []
            missing = []
        else:
            matched_set = user_set & job_set
            missing_set = job_set - user_set

            match_pct = round((len(matched_set) / len(job_set)) * 100, 1)

            matched = [s for s in job.skills if s.strip().lower() in matched_set]
            missing = [s for s in job.skills if s.strip().lower() in missing_set]

        results.append(
            MatchResult(
                job_id=job.job_id,
                title=job.title,
                company=job.company,
                match_percentage=match_pct,
                matched_skills=matched,
                missing_skills=missing,
            )
        )

    results.sort(key=lambda r: (-r.match_percentage, r.title))
    return MatchJobsResponse(results=results)
