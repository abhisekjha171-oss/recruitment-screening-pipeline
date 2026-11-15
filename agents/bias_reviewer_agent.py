"""Bias-guard Reviewer Agent — flags protected attributes in rationales and
verifies the ranking is score-consistent. Its flag does NOT silently rewrite
the rank; it appends bias_flags to the candidate and logs the finding so a
human reviewer can act. This preserves auditability."""
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.functions import kernel_function
from shared_state import CandidatePool
from tools.bias_tools import scan_for_protected_attributes, check_ranking_consistency

AGENT_NAME = "BiasReviewerAgent"


class BiasReviewerSkills:
    def __init__(self, pool: CandidatePool):
        self.pool = pool

    @kernel_function(description="Scan a text for protected attributes")
    def scan(self, text: str) -> list:
        return scan_for_protected_attributes(text)

    @kernel_function(description="Verify ranking is score-monotonic")
    def consistency(self) -> dict:
        payload = [
            {
                "candidate_id": c.candidate_id,
                "rank": c.rank,
                "match_score": c.match_score,
            }
            for c in self.pool.candidates
        ]
        return check_ranking_consistency(payload)


def build_bias_reviewer_agent(pool: CandidatePool, kernel=None):
    skills = BiasReviewerSkills(pool)
    agent = ChatCompletionAgent(
        name=AGENT_NAME,
        instructions=(
            "You are the Bias-guard Reviewer. Scan every rationale for protected "
            "attributes. Also verify the ranking is monotonic in score. Report "
            "flags; do NOT re-rank."
        ),
        kernel=kernel,
        plugins=[skills],
    )
    return agent, skills


def run_bias_reviewer(pool: CandidatePool, skills: BiasReviewerSkills):
    total_flags = 0
    for cand in pool.candidates:
        if not cand.rank_rationale:
            continue
        hits = skills.scan(cand.rank_rationale)
        if hits:
            cand.bias_flags = hits
            total_flags += len(hits)
            pool.log(
                AGENT_NAME,
                f"FLAG {cand.candidate_id}: rationale mentions protected "
                f"attribute(s) {hits}",
            )
    consistency = skills.consistency()
    if not consistency["consistent"]:
        for v in consistency["violations"]:
            pool.log(AGENT_NAME, f"RANKING INCONSISTENCY: {v}")
    else:
        pool.log(AGENT_NAME, "ranking is score-consistent")
    pool.log(AGENT_NAME, f"review complete: {total_flags} bias flag(s)")
    for cand in pool.candidates:
        if cand.rank is not None:
            cand.stage_status = "reviewed"