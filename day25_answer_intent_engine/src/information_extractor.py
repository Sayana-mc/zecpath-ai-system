import re


KNOWN_SKILLS = [
    "Python",
    "SQL",
    "Excel",
    "Power BI",
    "Tableau",
    "R",
    "SAS",
    "Java",
    "JavaScript",
    "React",
    "Node.js",
    "C++",
    "C#",
    "TensorFlow",
    "PyTorch",
    "Pandas",
    "NumPy",
    "Scikit-learn",
    "MongoDB",
    "MySQL",
    "Git",
    "GitHub"
]


def extract_skills(text):

    found_skills = []

    for skill in KNOWN_SKILLS:

        pattern = r"(?<!\w)" + re.escape(skill) + r"(?!\w)"

        if re.search(
            pattern,
            text,
            re.IGNORECASE
        ):
            found_skills.append(skill)

    return found_skills


def extract_experience(text):

    experience_values = []
    seen = set()

    patterns = [
        r"(\d+(?:\.\d+)?)\s*\+?\s*years?",
        r"(\d+(?:\.\d+)?)\s*\+?\s*year",
        r"(\d+)\s*months?"
    ]

    for pattern in patterns:

        matches = re.findall(
            pattern,
            text.lower()
        )

        for match in matches:
            if match not in seen:
                seen.add(match)
                experience_values.append(match)

    internship = bool(
        re.search(
            r"\bintern(ship)?\b",
            text,
            re.IGNORECASE
        )
    )

    return {
        "values": experience_values,
        "internship_mentioned": internship
    }


def extract_availability(text):

    lower_text = text.lower()

    if "immediately" in lower_text:
        return {
            "status": "immediate",
            "notice_period": None
        }

    notice_match = re.search(
        r"(\d+)\s*(day|days|month|months)"
        r"\s*(notice|notice period)",
        lower_text
    )

    if notice_match:

        return {
            "status": "notice_period",
            "notice_period": (
                f"{notice_match.group(1)} "
                f"{notice_match.group(2)}"
            )
        }

    if "available" in lower_text:
        return {
            "status": "available",
            "notice_period": None
        }

    return {
        "status": "unknown",
        "notice_period": None
    }


def extract_salary(text):

    lower_text = text.lower()

    lpa_match = re.search(
        r"(\d+(?:\.\d+)?)\s*(?:lpa|lakhs?|lakh)",
        lower_text
    )

    if lpa_match:

        return {
            "amount": float(lpa_match.group(1)),
            "unit": "LPA"
        }

    salary_match = re.search(
        r"(?:₹|rs\.?|inr)\s*"
        r"(\d+(?:,\d+)*(?:\.\d+)?)",
        lower_text
    )

    if salary_match:

        amount = salary_match.group(1).replace(
            ",",
            ""
        )

        return {
            "amount": float(amount),
            "unit": "INR"
        }

    return {
        "amount": None,
        "unit": None
    }


def extract_information(intent, text):

    information = {}

    if intent == "skills":
        information["skills"] = extract_skills(text)

    elif intent == "experience":
        information["experience"] = extract_experience(text)

    elif intent == "availability":
        information["availability"] = extract_availability(text)

    elif intent == "salary_expectation":
        information["salary_expectation"] = extract_salary(text)

    return information