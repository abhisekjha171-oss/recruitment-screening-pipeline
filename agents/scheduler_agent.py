"""Scheduler Agent — assigns interview slots to top-N ranked candidates."""
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.functions import kernel_function
from shared_state import CandidatePool
from tools.scheduling_tools import get_available_slots, assign_slot

AGENT_NAME = "SchedulerAgent"


class SchedulerSkills:
    def __init__(self, pool: CandidatePool, availability: dict):
        self.pool = pool
        self.availability = availability
        self.taken = set()

    @kernel_function(description="Get a candidate's available interview slots")
    def slots_for(self, candidate_id: str) -> list:
        return get_available_slots(self.availability, candidate_id)

    @kernel_function(description="Assign the first mutually-free slot")
    def assign(self, candidate_id: str) -> str:
        prefs = self.slots_for(candidate_id)
        return assign_slot(candidate_id, prefs, self.taken)


def build_scheduler_agent(pool: CandidatePool, skills: SchedulerSkills, kernel=None):
    agent = ChatCompletionAgent(
        name=AGENT_NAME,
        instructions=(
            "You are the Scheduler Agent. For the top-N ranked candidates only, "
            "assign the first mutually-free interview slot. If none is available, "
            "say so explicitly — never double-book."
        ),
        kernel=kernel,
        plugins=[skills],
    )
    return agent


def run_scheduler(pool: CandidatePool, skills: SchedulerSkills):
    ranked = [c for c in pool.candidates if c.rank is not None]
    ranked.sort(key=lambda c: c.rank)
    top_n = ranked[: pool.shortlist_size]
    for cand in top_n:
        slot = skills.assign(cand.candidate_id)
        if slot:
            cand.interview_slot = slot
            cand.stage_status = "scheduled"
            pool.log(AGENT_NAME, f"{cand.candidate_id} -> slot {slot}")
        else:
            pool.log(
                AGENT_NAME,
                f"{cand.candidate_id} -> NO SLOT AVAILABLE (escalate to human)",
            )
    for cand in ranked[pool.shortlist_size:]:
        pool.log(
            AGENT_NAME,
            f"{cand.candidate_id} not shortlisted (rank {cand.rank})",
        )