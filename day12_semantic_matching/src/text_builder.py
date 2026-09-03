def build_resume_text(resume):
    """
    Build a searchable text representation from
    Day 11 structured resume data.
    """

    parts = []

    academic_profile = resume.get(
        "academic_profile",
        {}
    )

    education = academic_profile.get(
        "education",
        []
    )

    certifications = academic_profile.get(
        "certifications",
        []
    )

    for record in education:
        parts.append(
            str(record.get("degree_type", ""))
        )
        parts.append(
            str(record.get("degree_name", ""))
        )
        parts.append(
            str(record.get("field_of_study", ""))
        )
        parts.append(
            str(record.get("institution", ""))
        )

    for certification in certifications:
        parts.append(
            str(certification.get("name", ""))
        )

    # Also support Day 9 skill data if available.
    skill_extraction = resume.get(
        "skill_extraction",
        {}
    )

    skills = skill_extraction.get(
        "skills",
        []
    )

    for skill in skills:
        parts.append(
            str(skill.get("skill", ""))
        )

    return " ".join(
        part for part in parts
        if part and part != "None"
    ).strip()


def build_job_text(job):
    """
    Build searchable text from a job description.
    """

    title = job.get(
        "job_title",
        ""
    )

    description = job.get(
        "description",
        ""
    )

    return f"{title}. {description}".strip()