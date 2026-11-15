"""Bias-guard Reviewer tools — check ranking for protected attributes."""
from typing import List, Dict

PROTECTED_ATTRIBUTES = [
    "gender", "male", "female", "non-binary", "age", "race", "ethnicity",
    "religion", "nationality", "marital status", "married", "single",
    "pregnant", "disability", "disabled", "veteran", "sexual orientation",
    "caste", "casteism", "skin colour", "skin color",
]


def scan_for_protected_attributes(text: str) -> List[str]:
    """Tool 1: return any protected-attribute keywords found in the text."""
    lower = text.lower()
    hits = [attr for attr in PROTECTED_ATTRIBUTES if attr in lower]
    return sorted(set(hits))


def check_ranking_consistency(candidates: List[Dict]) -> Dict:
    """Tool 2: verify scores are strictly monotonic with rank (no hand-edits)."""
    ranked = [c for c in candidates if c.get("rank") is not None]
    ranked.sort(key=lambda c: c["rank"])
    violations = []
    for i in range(1, len(ranked)):
        prev, cur = ranked[i - 1], ranked[i]
        if cur["match_score"] > prev["match_score"]:
            violations.append(
                f"rank {cur['rank']} ({cur['candidate_id']}) score "
                f"{cur['match_score']} > rank {prev['rank']} "
                f"({prev['candidate_id']}) score {prev['match_score']}"
            )
    return {"consistent": len(violations) == 0, "violations": violations}