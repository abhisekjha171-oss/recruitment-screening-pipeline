"""Parser Agent tools — plain Python, no LLM inside."""
import re

SKILL_KEYWORDS = [
    "python", "java", "javascript", "typescript", "sql", "aws", "azure", "gcp",
    "docker", "kubernetes", "react", "node", "django", "flask", "fastapi",
    "machine learning", "pytorch", "tensorflow", "scikit-learn", "pandas",
    "spark", "kafka", "terraform", "git", "agile", "rest", "graphql",
    "postgresql", "mongodb", "redis", "linux", "ci/cd", "jenkins",
]


def extract_contact_info(resume_text: str) -> dict:
    """Tool 1: pull name and email out of raw resume text."""
    email_match = re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", resume_text)
    # Name heuristic: first non-empty line that isn't an email
    lines = [ln.strip() for ln in resume_text.splitlines() if ln.strip()]
    name = ""
    for ln in lines:
        if "@" not in ln and len(ln.split()) <= 5:
            name = ln
            break
    return {"name": name, "email": email_match.group(0) if email_match else ""}


def extract_skills_experience_education(resume_text: str) -> dict:
    """Tool 2: extract skills, years of experience, and education level."""
    lower = resume_text.lower()
    skills = sorted({kw for kw in SKILL_KEYWORDS if kw in lower})

    # Years of experience: look for "X years" or "X+ years"
    exp_match = re.search(r"(\d+(?:\.\d+)?)\s*\+?\s*years?", lower)
    years = float(exp_match.group(1)) if exp_match else 0.0

    # Education
    education = "Unknown"
    for level, pattern in [
        ("PhD", r"\bph\.?d\b"),
        ("Masters", r"\bmaster'?s?\b|\bm\.?s\.?\b|\bm\.?tech\b"),
        ("Bachelors", r"\bbachelor'?s?\b|\bb\.?s\.?\b|\bb\.?tech\b"),
    ]:
        if re.search(pattern, lower):
            education = level
            break
    return {"skills": skills, "years_experience": years, "education": education}