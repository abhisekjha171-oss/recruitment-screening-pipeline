"""Matcher Agent — scores each parsed profile against the JD requirements."""
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.functions import kernel_function
from shared_state import CandidatePool
from tools.matching_tools import (
    compute_skill_match_score,
    compute_experience_education_score,
)

AGENT_NAME = "MatcherAgent"


class MatcherSkills:
    def __init__(self, pool: CandidatePool):
        self.pool = pool

    @kernel_function(description="Score skill overlap vs named JD requirements")
    def score_skills(self, candidate_id: str) -> dict:
        c = self.pool.get_by_id(candidate_id)
        return compute_skill_match_score(
            self.pool.job_description["required_skills"], c.skills
        )

    @kernel_function(description="Score experience and education vs JD minimums")
    def score_exp_edu(self, candidate_id: str) -> dict:
        c = self.pool.get_by_id(candidate_id)
        profile = {"years_experience": c.years_experience, "education": c.education}
        return compute_experience_education_score(self.pool.job_description, profile)


def build_matcher_agent(pool: CandidatePool, kernel=None):
    skills = MatcherSkills(pool)
    agent = ChatCompletionAgent(
        name=AGENT_NAME,
        instructions=(
            "You are the Matcher Agent. For each candidate, call both tools and "
            "combine into a final score: 0.6*skill + 0.3*experience + 0.1*education. "
            "Justify each score against NAMED JD requirements (matched vs missing)."
        ),
        kernel=kernel,
        plugins=[skills],
    )
    return agent, skills


def run_matcher(pool: CandidatePool, skills: MatcherSkills):
    jd_skills = pool.job_description["required_skills"]
    for cand in pool.candidates:
        skill_res = skills.score_skills(cand.candidate_id)
        exp_res = skills.score_exp_edu(cand.candidate_id)
        final = (
            0.6 * skill_res["score"]
            + 0.3 * exp_res["experience_score"]
            + 0.1 * exp_res["education_score"]
        )
        cand.match_score = round(final, 3)
        cand.match_justification = {
            "final_score": cand.match_score,
            "matched_requirements": skill_res["matched"],
            "missing_requirements": skill_res["missing"],
            "skill_score": skill_res["score"],
            "experience_score": exp_res["experience_score"],
            "education_score": exp_res["education_score"],
            "years_experience": exp_res["candidate_years"],
            "required_years": exp_res["required_years"],
            "named_jd_requirements": jd_skills,
        }
        cand.stage_status = "matched"
        pool.log(
            AGENT_NAME,
            f"{cand.candidate_id} matched {len(skill_res['matched'])}/"
            f"{len(jd_skills)} named reqs -> score {cand.match_score}",
        )