"""Parser Agent — extracts structured profile from raw resume."""
from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.functions import kernel_function
from shared_state import CandidatePool
from tools.parsing_tools import extract_contact_info, extract_skills_experience_education

AGENT_NAME = "ParserAgent"


class ParserSkills:
    def __init__(self, pool: CandidatePool):
        self.pool = pool

    @kernel_function(description="Extract name and email from resume text")
    def get_contact(self, resume_text: str) -> dict:
        return extract_contact_info(resume_text)

    @kernel_function(description="Extract skills, experience, education")
    def get_profile(self, resume_text: str) -> dict:
        return extract_skills_experience_education(resume_text)


def build_parser_agent(pool: CandidatePool, kernel=None):
    skills = ParserSkills(pool)
    agent = ChatCompletionAgent(
        name=AGENT_NAME,
        instructions=(
            "You are the Parser Agent. Your only job is to convert raw resume "
            "text into a structured profile using your two tools. Do not score "
            "or rank candidates."
        ),
        kernel=kernel,
        plugins=[skills],
    )
    return agent, skills


def run_parser(pool: CandidatePool, skills: ParserSkills):
    for cand in pool.candidates:
        contact = skills.get_contact(cand.raw_resume_text)
        profile = skills.get_profile(cand.raw_resume_text)
        cand.name = contact["name"]
        cand.email = contact["email"]
        cand.skills = profile["skills"]
        cand.years_experience = profile["years_experience"]
        cand.education = profile["education"]
        cand.stage_status = "parsed"
        pool.log(
            AGENT_NAME,
            f"parsed {cand.candidate_id}: {len(cand.skills)} skills, "
            f"{cand.years_experience}y, {cand.education}",
        )