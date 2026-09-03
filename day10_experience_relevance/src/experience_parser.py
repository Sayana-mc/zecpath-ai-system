import re
from datetime import date
from typing import Optional


MONTHS = {
    "jan": 1,
    "january": 1,
    "feb": 2,
    "february": 2,
    "mar": 3,
    "march": 3,
    "apr": 4,
    "april": 4,
    "may": 5,
    "jun": 6,
    "june": 6,
    "jul": 7,
    "july": 7,
    "aug": 8,
    "august": 8,
    "sep": 9,
    "sept": 9,
    "september": 9,
    "oct": 10,
    "october": 10,
    "nov": 11,
    "november": 11,
    "dec": 12,
    "december": 12,
}


def normalize_text(text: str) -> str:
    """Normalize resume experience text."""

    if not text:
        return ""

    text = text.replace("\u2013", "-")
    text = text.replace("\u2014", "-")
    text = text.replace("\u2012", "-")

    text = re.sub(r"[ \t]+", " ", text)

    return text.strip()


def parse_month_year(value: str) -> Optional[date]:
    """Convert month/year text into a date object."""

    if not value:
        return None

    value = value.strip().lower()

    if value in {"present", "current", "now"}:
        today = date.today()
        return date(today.year, today.month, 1)

    match = re.search(
        r"(jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|"
        r"may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:t(?:ember)?)?|"
        r"oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)"
        r"\s+(\d{4})",
        value,
        re.IGNORECASE,
    )

    if match:
        month_name = match.group(1).lower()
        year = int(match.group(2))
        month = MONTHS[month_name]
        return date(year, month, 1)

    match = re.search(r"\b(\d{1,2})/(\d{4})\b", value)

    if match:
        month = int(match.group(1))
        year = int(match.group(2))

        if 1 <= month <= 12:
            return date(year, month, 1)

    match = re.search(r"\b(\d{4})\b", value)

    if match:
        year = int(match.group(1))
        return date(year, 1, 1)

    return None


def calculate_months(start: Optional[date], end: Optional[date]) -> int:
    """Calculate approximate employment duration in months."""

    if not start or not end:
        return 0

    months = (
        (end.year - start.year) * 12
        + (end.month - start.month)
        + 1
    )

    return max(months, 0)


def parse_date_range(text: str):
    """Extract start and end dates from a text line."""

    if not text:
        return None, None

    normalized = normalize_text(text)

    pattern = re.compile(
        r"("
        r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|"
        r"May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|"
        r"Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
        r"\s+\d{4}"
        r"|"
        r"\d{1,2}/\d{4}"
        r"|"
        r"\d{4}"
        r")"
        r"\s*(?:-|to)\s*"
        r"("
        r"(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|"
        r"May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:t(?:ember)?)?|"
        r"Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?)"
        r"\s+\d{4}"
        r"|"
        r"\d{1,2}/\d{4}"
        r"|"
        r"\d{4}"
        r"|"
        r"Present|Current|Now"
        r")",
        re.IGNORECASE,
    )

    match = pattern.search(normalized)

    if not match:
        return None, None

    start = parse_month_year(match.group(1))
    end = parse_month_year(match.group(2))

    return start, end


def detect_role_line(line: str) -> bool:
    """Check whether a line looks like a job title."""

    if not line:
        return False

    lowered = line.lower()

    role_keywords = [
        "developer",
        "engineer",
        "analyst",
        "manager",
        "executive",
        "designer",
        "teacher",
        "consultant",
        "specialist",
        "associate",
        "intern",
        "administrator",
        "officer",
        "lead",
        "architect",
        "scientist",
        "accountant",
        "recruiter",
        "coordinator",
        "supervisor",
    ]

    return any(
        keyword in lowered
        for keyword in role_keywords
    )


def extract_company_from_line(line: str) -> Optional[str]:
    """Extract company name when it appears after '- at ' or similar patterns."""

    if not line:
        return None

    patterns = [
        r"\bat\s+(.+)$",
        r"\b-\s+(.+)$",
        r",\s+(.+)$",
    ]

    for pattern in patterns:
        match = re.search(
            pattern,
            line,
            re.IGNORECASE,
        )

        if match:
            company = match.group(1).strip()

            if len(company) > 2:
                return company

    return None


def parse_experience_section(text: str):
    """Parse a WORK EXPERIENCE section into structured records."""

    lines = [
        normalize_text(line)
        for line in text.splitlines()
        if normalize_text(line)
    ]

    experiences = []

    current_role = None
    current_company = None

    for index, line in enumerate(lines):

        start, end = parse_date_range(line)

        if start and end:

            if current_role:

                experiences.append(
                    {
                        "job_title": current_role,
                        "company": current_company,
                        "start_date": start.isoformat(),
                        "end_date": end.isoformat(),
                        "duration_months": calculate_months(
                            start,
                            end,
                        ),
                    }
                )

            current_role = None
            current_company = None
            continue

        if detect_role_line(line):

            current_role = line
            current_company = extract_company_from_line(line)

            if not current_company and index + 1 < len(lines):
                next_line = lines[index + 1]

                if not parse_date_range(next_line)[0]:
                    current_company = next_line

    return experiences


def calculate_total_experience(experiences) -> float:
    """Calculate total experience in years."""

    total_months = sum(
        item.get("duration_months", 0)
        for item in experiences
    )

    return round(total_months / 12, 2)


def detect_gaps(experiences):
    """Detect gaps between sequential employment periods."""

    valid = []

    for item in experiences:

        start = parse_month_year(
            item.get("start_date", "")
        )

        end = parse_month_year(
            item.get("end_date", "")
        )

        if start and end:
            valid.append((start, end, item))

    valid.sort(key=lambda x: x[0])

    gaps = []

    for previous, current in zip(valid, valid[1:]):

        previous_end = previous[1]
        current_start = current[0]

        months = (
            (current_start.year - previous_end.year) * 12
            + (current_start.month - previous_end.month)
            - 1
        )

        if months > 0:

            gaps.append(
                {
                    "from": previous_end.isoformat(),
                    "to": current_start.isoformat(),
                    "gap_months": months,
                }
            )

    return gaps


def detect_overlaps(experiences):
    """Detect overlapping employment periods."""

    valid = []

    for item in experiences:

        start = parse_month_year(
            item.get("start_date", "")
        )

        end = parse_month_year(
            item.get("end_date", "")
        )

        if start and end:
            valid.append((start, end, item))

    overlaps = []

    for index, first in enumerate(valid):

        for second in valid[index + 1:]:

            first_start, first_end, first_item = first
            second_start, second_end, second_item = second

            if (
                first_start <= second_end
                and second_start <= first_end
            ):

                overlaps.append(
                    {
                        "role_1": first_item.get("job_title"),
                        "role_2": second_item.get("job_title"),
                        "overlap": True,
                    }
                )

    return overlaps