"""Matcher Agent tools — rule-based scoring against named JD requirements."""
from typing import Dict, List


def compute_skill_match_score(required: List[str], candidate_skills: List[str]) -> dict:
    """Tool 1: weighted skill overlap against named JD requirements."""
    req = {s.lower() for s in required}
    have = {s.lower() for s in candidate_skills}
    matched = sorted(req & have)
    missing = sorted(req - have)
    score = len(matched) / len(req) if req else 0.0
    return {
        "score": round(score, 3),
        "matched": matched,
        "missing": missing,
    }


def compute_experience_education_score(jd: Dict, profile: Dict) -> dict:
    """Tool 2: score experience & education against JD minimums."""
    min_exp = float(jd.get("min_years_experience", 0))
    cand_exp = float(profile.get("years_experience", 0))
    exp_score = min(cand_exp / min_exp, 1.0) if min_exp > 0 else 1.0

    edu_rank = {"Unknown": 0, "Bachelors": 1, "Masters": 2, "PhD": 3}
    required_rank = edu_rank.get(jd.get("min_education", "Bachelors"), 1)
    cand_rank = edu_rank.get(profile.get("education", "Unknown"), 0)
    edu_score = 1.0 if cand_rank >= required_rank else 0.0

    return {
        "experience_score": round(exp_score, 3),
        "education_score": edu_score,
        "candidate_years": cand_exp,
        "required_years": min_exp,
    }