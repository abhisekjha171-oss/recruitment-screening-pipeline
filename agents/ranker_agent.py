"""Ranker Agent — orders matched candidates and writes a one-line rationale."""
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.functions import kernel_function
from shared_state import CandidatePool
from tools.ranking_tools import sort_by_score, build_rationale

AGENT_NAME = "RankerAgent"


class RankerSkills:
    def __init__(self, pool: CandidatePool):
        self.pool = pool

    @kernel_function(description="Sort candidates by final match score")
    def sort(self) -> list:
        data = [
            {"candidate_id": c.candidate_id, "final_score": c.match_score}
            for c in self.pool.candidates
        ]
        return sort_by_score(data)

    @kernel_function(description="Draft one-line rationale for a candidate")
    def rationale(self, candidate_id: str) -> str:
        c = self.pool.get_by_id(candidate_id)
        payload = {
            "matched_requirements": c.match_justification["matched_requirements"],
            "missing_requirements": c.match_justification["missing_requirements"],
            "years_experience": c.match_justification["years_experience"],
            "required_years": c.match_justification["required_years"],
        }
        return build_rationale(payload, self.pool.job_description["required_skills"])


def build_ranker_agent(pool: CandidatePool, kernel=None):
    skills = RankerSkills(pool)
    agent = ChatCompletionAgent(
        name=AGENT_NAME,
        instructions=(
            "You are the Ranker Agent. Sort candidates by score, then write a "
            "single-line rationale per candidate citing NAMED JD requirements. "
            "Do not re-score."
        ),
        kernel=kernel,
        plugins=[skills],
    )
    return agent, skills


def run_ranker(pool: CandidatePool, skills: RankerSkills):
    ordered = skills.sort()
    for rank_idx, row in enumerate(ordered, start=1):
        cand = pool.get_by_id(row["candidate_id"])
        cand.rank = rank_idx
        cand.rank_rationale = skills.rationale(cand.candidate_id)
        cand.stage_status = "ranked"
        pool.log(
            AGENT_NAME,
            f"rank {rank_idx}: {cand.candidate_id} (score {cand.match_score}) "
            f"- {cand.rank_rationale}",
        )