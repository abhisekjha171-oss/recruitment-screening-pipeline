"""Pipeline Coordinator — runs stages in order, passing the shared pool forward.
Sequential pipeline: Parser -> Matcher -> Ranker -> Scheduler -> [BiasReviewer]."""
from shared_state import CandidatePool, CandidateProfile
from agents.parser_agent import build_parser_agent, run_parser
from agents.matcher_agent import build_matcher_agent, run_matcher
from agents.ranker_agent import build_ranker_agent, run_ranker
from agents.scheduler_agent import (
    build_scheduler_agent,
    SchedulerSkills,
    run_scheduler,
)
from agents.bias_reviewer_agent import (
    build_bias_reviewer_agent,
    BiasReviewerSkills,
    run_bias_reviewer,
)

AGENT_NAME = "PipelineCoordinator"


def run_pipeline(
    job_description: dict,
    raw_resumes: list,
    availability: dict,
    shortlist_size: int = 3,
    kernel=None,
    enable_bias_reviewer: bool = True,
    log_path: str = "run_log.txt",
) -> CandidatePool:
    pool = CandidatePool(
        job_description=job_description,
        shortlist_size=shortlist_size,
        log_path=log_path,
    )
    for i, text in enumerate(raw_resumes):
        pool.add_candidate(
            CandidateProfile(candidate_id=f"C{i+1:03d}", raw_resume_text=text)
        )
    pool.log(
        AGENT_NAME,
        f"pipeline start: {len(pool.candidates)} candidates, "
        f"shortlist={shortlist_size}, bias_reviewer={enable_bias_reviewer}",
    )

    _, parser_skills = build_parser_agent(pool, kernel)
    run_parser(pool, parser_skills)

    _, matcher_skills = build_matcher_agent(pool, kernel)
    run_matcher(pool, matcher_skills)

    _, ranker_skills = build_ranker_agent(pool, kernel)
    run_ranker(pool, ranker_skills)

    sched_skills = SchedulerSkills(pool, availability)
    build_scheduler_agent(pool, sched_skills, kernel)
    run_scheduler(pool, sched_skills)

    if enable_bias_reviewer:
        _, bias_skills = build_bias_reviewer_agent(pool, kernel)
        run_bias_reviewer(pool, bias_skills)

    pool.log(AGENT_NAME, "pipeline complete")
    return pool