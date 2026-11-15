"""Scheduler Agent tools — slot assignment from availability table."""
from typing import List, Dict, Set


def get_available_slots(availability: Dict[str, List[str]], candidate_id: str) -> List[str]:
    """Tool 1: return the raw availability list for one candidate."""
    return availability.get(candidate_id, [])


def assign_slot(candidate_id: str, preferred: List[str], taken: Set[str]) -> str:
    """Tool 2: pick the first mutually-free slot; return '' if none."""
    for slot in preferred:
        if slot not in taken:
            taken.add(slot)
            return slot
    return ""