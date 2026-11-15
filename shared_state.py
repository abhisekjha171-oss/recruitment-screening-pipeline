"""
Shared candidate pool — the single blackboard every agent reads and writes.
This satisfies the Group 4 requirement: "shared candidate pool in memory
carried through every stage." No RAG, no vector store — plain in-memory state.
"""
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional
import datetime
import os


@dataclass
class CandidateProfile:
    candidate_id: str
    raw_resume_text: str = ""
    name: str = ""
    email: str = ""
    skills: List[str] = field(default_factory=list)
    years_experience: float = 0.0
    education: str = ""
    match_score: float = 0.0
    match_justification: Dict[str, Any] = field(default_factory=dict)
    rank: Optional[int] = None
    rank_rationale: str = ""
    interview_slot: Optional[str] = None
    bias_flags: List[str] = field(default_factory=list)
    stage_status: str = "raw"   # raw -> parsed -> matched -> ranked -> scheduled -> reviewed


@dataclass
class CandidatePool:
    job_description: Dict[str, Any] = field(default_factory=dict)
    candidates: List[CandidateProfile] = field(default_factory=list)
    shortlist_size: int = 3
    trace: List[str] = field(default_factory=list)
    log_path: str = "run_log.txt"

    def add_candidate(self, cand: CandidateProfile):
        self.candidates.append(cand)

    def get_by_id(self, cid: str) -> CandidateProfile:
        for c in self.candidates:
            if c.candidate_id == cid:
                return c
        raise KeyError(cid)

    def log(self, agent: str, message: str):
        ts = datetime.datetime.utcnow().isoformat(timespec="seconds")
        entry = f"[{ts}] [{agent}] {message}"
        self.trace.append(entry)
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(entry + "\n")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "job_description": self.job_description,
            "candidates": [asdict(c) for c in self.candidates],
            "trace": self.trace,
        }