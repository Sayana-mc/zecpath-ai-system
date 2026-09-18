import json


class RecruiterReportFormatter:
    """
    Converts the structured screening report
    into a recruiter-readable text report.
    """

    def __init__(self, report):
        self.report = report

    def format_text(self):

        metadata = self.report["report_metadata"]
        summary = self.report["screening_summary"]
        highlights = self.report["highlights"]
        behavioral = self.report["behavioral_summary"]

        lines = []

        lines.append("=" * 60)
        lines.append("AI SCREENING REPORT")
        lines.append("=" * 60)

        lines.append("")
        lines.append("CANDIDATE INFORMATION")
        lines.append("-" * 40)

        lines.append(
            f"Candidate ID : {metadata['candidate_id']}"
        )
        lines.append(
            f"Candidate    : {metadata['candidate_name']}"
        )
        lines.append(
            f"Job ID       : {metadata['job_id']}"
        )
        lines.append(
            f"Job Title    : {metadata['job_title']}"
        )

        lines.append("")
        lines.append("SCREENING SUMMARY")
        lines.append("-" * 40)

        lines.append(
            f"Total Score        : "
            f"{summary['total_score']}"
        )

        lines.append(
            f"Questions Evaluated: "
            f"{summary['questions_evaluated']}"
        )

        lines.append("")
        lines.append("KEY HIGHLIGHTS")
        lines.append("-" * 40)

        skills = highlights.get(
            "skill_confirmations",
            []
        )

        lines.append(
            "Confirmed Skills: "
            + (
                ", ".join(skills)
                if skills
                else "Not available"
            )
        )

        lines.append(
            "Availability: "
            + str(
                highlights.get("availability")
                or "Not available"
            )
        )

        salary = highlights.get(
            "salary_expectation"
        )

        lines.append(
            "Salary Expectation: "
            + (
                f"{salary} LPA"
                if salary is not None
                else "Not available"
            )
        )

        lines.append("")
        lines.append("STRENGTHS")
        lines.append("-" * 40)

        for strength in self.report["strengths"]:
            lines.append(f"- {strength}")

        lines.append("")
        lines.append("RISKS")
        lines.append("-" * 40)

        if self.report["risks"]:
            for risk in self.report["risks"]:
                lines.append(f"- {risk}")
        else:
            lines.append("- No major risks detected.")

        lines.append("")
        lines.append("MISSING DATA")
        lines.append("-" * 40)

        if self.report["missing_data"]:
            for item in self.report["missing_data"]:
                lines.append(f"- {item}")
        else:
            lines.append("- No missing data detected.")

        lines.append("")
        lines.append("BEHAVIORAL INDICATORS")
        lines.append("-" * 40)

        lines.append(
            f"Communication Strength: "
            f"{behavioral['communication_strength']}"
        )

        lines.append(
            f"Hesitation Count: "
            f"{behavioral['hesitation_count']}"
        )

        lines.append(
            f"Uncertainty Count: "
            f"{behavioral['uncertainty_count']}"
        )

        lines.append(
            f"Average Response Length: "
            f"{behavioral['average_response_length']}"
        )

        lines.append(
            f"Sentiment: "
            f"{behavioral['sentiment']}"
        )

        lines.append(
            f"Contradictions Detected: "
            f"{behavioral['contradictions_detected']}"
        )

        lines.append("")
        lines.append("=" * 60)
        lines.append("END OF AI SCREENING REPORT")
        lines.append("=" * 60)

        return "\n".join(lines)

    def save_json(self, path):
        with open(
            path,
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                self.report,
                file,
                indent=4
            )

    def save_text(self, path):
        with open(
            path,
            "w",
            encoding="utf-8"
        ) as file:
            file.write(
                self.format_text()
            )