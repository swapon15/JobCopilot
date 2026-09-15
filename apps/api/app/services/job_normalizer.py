import re

from app.domain import JobDescriptionCreate, NormalizedRequirement

SECTION_ENDINGS = {
    "benefits",
    "compensation",
    "about",
    "about us",
    "what we offer",
    "equal opportunity",
}

REQUIREMENT_HEADINGS = {
    "requirements",
    "required qualifications",
    "minimum qualifications",
    "basic qualifications",
    "qualifications",
    "what you bring",
    "you have",
}

PREFERRED_HEADINGS = {
    "preferred qualifications",
    "nice to have",
    "bonus points",
    "preferred skills",
}


def normalize_job_description(job: JobDescriptionCreate) -> JobDescriptionCreate:
    lines = _clean_lines(job.raw_description)

    return JobDescriptionCreate(
        raw_description=job.raw_description.strip(),
        source_url=job.source_url,
        title=job.title or _extract_labeled_value(lines, "title") or _infer_title(lines),
        company=job.company or _extract_labeled_value(lines, "company"),
        location=(
            job.location or _extract_labeled_value(lines, "location") or _infer_location(lines)
        ),
        compensation=job.compensation or _extract_compensation(job.raw_description),
        work_mode=job.work_mode or _infer_work_mode(job.raw_description),
    )


def extract_requirements(raw_description: str) -> list[NormalizedRequirement]:
    lines = _clean_lines(raw_description)
    requirements: list[NormalizedRequirement] = []
    in_requirements = False
    preferred_section = False

    for line in lines:
        heading = _normalized_heading(line)
        if heading in PREFERRED_HEADINGS:
            in_requirements = True
            preferred_section = True
            continue
        if heading in REQUIREMENT_HEADINGS:
            in_requirements = True
            preferred_section = False
            continue
        if heading in SECTION_ENDINGS:
            in_requirements = False
            preferred_section = False
            continue

        bullet_text = _strip_bullet(line)
        if not bullet_text:
            continue

        if in_requirements or _looks_like_requirement(bullet_text):
            requirements.append(
                NormalizedRequirement(
                    text=bullet_text,
                    mandatory=not preferred_section and not _looks_preferred(bullet_text),
                )
            )

    return _dedupe_requirements(requirements)


def _clean_lines(raw_description: str) -> list[str]:
    return [line.strip() for line in raw_description.splitlines() if line.strip()]


def _extract_labeled_value(lines: list[str], label: str) -> str | None:
    pattern = re.compile(rf"^{re.escape(label)}\s*:\s*(.+)$", re.IGNORECASE)
    for line in lines:
        match = pattern.match(line)
        if match:
            return match.group(1).strip()
    return None


def _infer_title(lines: list[str]) -> str | None:
    for line in lines[:5]:
        if ":" not in line and len(line) <= 120 and not line.startswith(("-", "*", "•")):
            return line
    return None


def _infer_location(raw_lines: list[str]) -> str | None:
    for line in raw_lines:
        if re.search(r"\b(remote|hybrid|onsite|on-site|united states|usa|u\.s\.)\b", line, re.I):
            if len(line) <= 200:
                return line
    return None


def _extract_compensation(raw_description: str) -> str | None:
    salary_range = re.search(
        r"(\$[\d,]+(?:\s*-\s*\$?[\d,]+)?(?:\s*(?:per year|annually|/year|base)?)?)",
        raw_description,
        re.IGNORECASE,
    )
    if salary_range:
        return salary_range.group(1).strip()
    return None


def _infer_work_mode(raw_description: str) -> str | None:
    text = raw_description.lower()
    if "remote" in text:
        return "remote"
    if "hybrid" in text:
        return "hybrid"
    if "onsite" in text or "on-site" in text:
        return "onsite"
    return None


def _normalized_heading(line: str) -> str:
    return line.strip().strip(":").lower()


def _strip_bullet(line: str) -> str:
    return re.sub(r"^\s*(?:[-*•]|\d+[.)])\s*", "", line).strip()


def _looks_like_requirement(text: str) -> bool:
    return bool(
        re.search(
            r"\b(required|requirement|must|experience with|years of|proficiency|familiarity)\b",
            text,
            re.IGNORECASE,
        )
    )


def _looks_preferred(text: str) -> bool:
    return bool(re.search(r"\b(preferred|nice to have|bonus|plus)\b", text, re.IGNORECASE))


def _dedupe_requirements(requirements: list[NormalizedRequirement]) -> list[NormalizedRequirement]:
    seen: set[str] = set()
    deduped: list[NormalizedRequirement] = []
    for requirement in requirements:
        key = requirement.text.lower()
        if key not in seen:
            seen.add(key)
            deduped.append(requirement)
    return deduped
