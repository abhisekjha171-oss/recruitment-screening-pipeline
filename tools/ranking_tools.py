"""Ranker Agent tools — deterministic ordering + rationale drafting."""
from typing import List, Dict


def sort_by_score(scored: List[Dict]) -> List[Dict]:
    """Tool 1: sort candidates by combined match score, descending."""
    return sorted(scored, key=lambda c: c["final_score"], reverse=True)


def build_rationale(candidate: Dict, jd_requirements: List[str]) -> str:
    """Tool 2: compose a one-line rationale tied to named requirements."""
    matched = candidate.get("matched_requirements", [])
    missing = candidate.get("missing_requirements", [])
    parts = []
    if matched:
        parts.append(f"meets {len(matched)}/{len(jd_requirements)} requirements ({', '.join(matched[:3])})")
    if missing:
        parts.append(f"lacks {', '.join(missing[:3])}")
    if candidate.get("years_experience", 0) >= candidate.get("required_years", 0):
        parts.append(f"{candidate['years_experience']}y exp meets minimum")
    else:
        parts.append(f"{candidate['years_experience']}y exp below minimum")
    return "; ".join(parts)