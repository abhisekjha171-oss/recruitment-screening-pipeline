"""Scenarios: happy path, missing-experience edge, slot collision,
and bias-reviewer behavior."""
import json
import os
import pytest
from agents.pipeline_coordinator import run_pipeline

HERE = os.path.dirname(__file__)
DATA = os.path.join(HERE, "..", "data")


def load():
    with open(os.path.join(DATA, "job_description.json")) as f:
        jd = json.load(f)
    with open(os.path.join(DATA, "resumes.json")) as f:
        resumes = json.load(f)["resumes"]
    with open(os.path.join(DATA, "availability.json")) as f:
        avail = json.load(f)
    return jd, resumes, avail


@pytest.fixture
def log_path(tmp_path):
    return str(tmp_path / "test_run_log.txt")


def test_happy_path_ranking_and_scheduling(log_path):
    jd, resumes, avail = load()
    pool = run_pipeline(jd, resumes, avail, shortlist_size=3, log_path=log_path)
    ranked = sorted([c for c in pool.candidates if c.rank], key=lambda c: c.rank)
    assert ranked[0].name == "Alice Nguyen"
    assert ranked[0].interview_slot is not None
    assert len([c for c in pool.candidates if c.interview_slot]) == 3
    assert "requirements" in ranked[0].rank_rationale


def test_missing_experience_does_not_crash(log_path):
    jd, resumes, avail = load()
    pool = run_pipeline(jd, resumes, avail, log_path=log_path)
    dan = next(c for c in pool.candidates if c.name == "Dan Wu")
    assert dan.years_experience == 0.0
    assert dan.match_score < 0.7
    assert dan.rank is not None


def test_slot_collision_and_no_slot_escalation(log_path):
    jd, resumes, avail = load()
    pool = run_pipeline(jd, resumes, avail, shortlist_size=5, log_path=log_path)
    scheduled = [c for c in pool.candidates if c.interview_slot]
    slots = [c.interview_slot for c in scheduled]
    assert len(slots) == len(set(slots))
    assert any("NO SLOT AVAILABLE" in line for line in pool.trace)


def test_bias_reviewer_flags_protected_attribute(log_path):
    jd, resumes, avail = load()
    pool = run_pipeline(jd, resumes, avail, log_path=log_path)
    # Every candidate should have stage_status 'reviewed'
    assert all(c.stage_status == "reviewed" for c in pool.candidates if c.rank)
    # Simulate an injected biased rationale, then re-run reviewer
    from agents.bias_reviewer_agent import BiasReviewerSkills, run_bias_reviewer
    target = sorted([c for c in pool.candidates if c.rank], key=lambda c: c.rank)[0]
    target.rank_rationale += " (female candidate, age 29)"
    skills = BiasReviewerSkills(pool)
    run_bias_reviewer(pool, skills)
    assert "female" in target.bias_flags
    assert "age" in target.bias_flags


def test_ranking_consistency_check(log_path):
    jd, resumes, avail = load()
    pool = run_pipeline(jd, resumes, avail, log_path=log_path)
    from tools.bias_tools import check_ranking_consistency
    payload = [
        {"candidate_id": c.candidate_id, "rank": c.rank, "match_score": c.match_score}
        for c in pool.candidates
    ]
    assert check_ranking_consistency(payload)["consistent"]