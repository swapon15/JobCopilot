import re

from app.domain import CandidateEvidenceBase, CandidateProfileCreate, ExperienceType

KNOWN_SKILLS = [
    "Python",
    "TypeScript",
    "JavaScript",
    "React",
    "Next.js",
    "FastAPI",
    "SQL",
    "PostgreSQL",
    "Docker",
    "Kubernetes",
    "AWS",
    "Azure",
    "GCP",
    "Snowflake",
    "Machine Learning",
    "ML",
    "Data Engineering",
    "C++",
]


def draft_candidate_profile(raw_text: str) -> CandidateProfileCreate:
    lines = [line.strip(" -\t") for line in raw_text.splitlines() if line.strip()]
    headline = _headline(lines)
    skills = _skills(raw_text)
    summary = _summary(lines, skills)
    target_roles = _target_roles(raw_text, headline)
    preferred_locations = _preferred_locations(raw_text)
    work_preferences = _work_preferences(raw_text, preferred_locations)

    return CandidateProfileCreate(
        headline=headline,
        summary=summary,
        target_roles=target_roles,
        preferred_locations=preferred_locations,
        work_preferences=work_preferences,
        sponsorship_required=_sponsorship_required(raw_text),
        evidence=[
            CandidateEvidenceBase(
                project_or_position=_evidence_title(lines, headline),
                description=_evidence_description(lines, summary),
                skills=skills,
                responsibilities=_responsibilities(lines),
                measurable_outcomes=_outcomes(lines),
                experience_type=ExperienceType.direct,
            )
        ],
    )


def _headline(lines: list[str]) -> str:
    for line in lines:
        if len(line) <= 120 and not _looks_like_section_header(line):
            return line
    return "Candidate Profile"


def _summary(lines: list[str], skills: list[str]) -> str:
    summary_lines = [
        line
        for line in lines[:6]
        if not _looks_like_section_header(line) and not line.lower().startswith("skills")
    ]
    summary = " ".join(summary_lines[:3]).strip()
    if summary:
        return summary
    if skills:
        return f"Experienced candidate with skills in {', '.join(skills[:5])}."
    return "Draft summary generated from pasted profile text."


def _target_roles(raw_text: str, headline: str) -> list[str]:
    role_patterns = [
        r"(principal|staff|senior|lead)\s+(software|platform|data|ml|ai)\s+engineer",
        r"(software|platform|data|ml|ai)\s+engineer",
        r"engineering\s+manager",
    ]
    found: list[str] = []
    for pattern in role_patterns:
        for match in re.finditer(pattern, raw_text, flags=re.IGNORECASE):
            role = match.group(0).title().replace("Ml", "ML").replace("Ai", "AI")
            if role not in found:
                found.append(role)
    return found[:4] or [headline]


def _preferred_locations(raw_text: str) -> list[str]:
    lower_text = raw_text.lower()
    locations: list[str] = []
    if "remote" in lower_text:
        locations.append("Remote")
    if "hybrid" in lower_text:
        locations.append("Hybrid")
    return locations or ["Remote"]


def _work_preferences(raw_text: str, preferred_locations: list[str]) -> list[str]:
    preferences = list(preferred_locations)
    lower_text = raw_text.lower()
    if "work-life" in lower_text or "work life" in lower_text:
        preferences.append("Strong work-life balance")
    if "async" in lower_text:
        preferences.append("Async-friendly team")
    return preferences


def _sponsorship_required(raw_text: str) -> bool:
    lower_text = raw_text.lower()
    return "sponsorship required" in lower_text or "require sponsorship" in lower_text


def _skills(raw_text: str) -> list[str]:
    lower_text = raw_text.lower()
    skills = [skill for skill in KNOWN_SKILLS if skill.lower() in lower_text]
    return skills[:10]


def _evidence_title(lines: list[str], headline: str) -> str:
    for line in lines:
        if any(
            keyword in line.lower() for keyword in ["project", "platform", "system", "engineer"]
        ):
            return line[:200]
    return headline[:200]


def _evidence_description(lines: list[str], summary: str) -> str:
    evidence_lines = [
        line
        for line in lines
        if any(
            keyword in line.lower()
            for keyword in ["built", "led", "created", "designed", "implemented", "improved"]
        )
    ]
    return " ".join(evidence_lines[:3]) or summary


def _responsibilities(lines: list[str]) -> list[str]:
    responsibilities = [
        line
        for line in lines
        if any(keyword in line.lower() for keyword in ["owned", "led", "designed", "managed"])
    ]
    return responsibilities[:5]


def _outcomes(lines: list[str]) -> list[str]:
    outcomes = [
        line
        for line in lines
        if re.search(r"\d+%|\$|reduced|increased|improved|minutes|hours", line, re.IGNORECASE)
    ]
    return outcomes[:5]


def _looks_like_section_header(line: str) -> bool:
    return line.endswith(":") or line.lower() in {
        "experience",
        "skills",
        "projects",
        "education",
        "summary",
    }
