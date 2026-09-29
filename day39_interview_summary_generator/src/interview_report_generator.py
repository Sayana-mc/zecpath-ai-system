class InterviewReportGenerator:
    """
    Generates recruiter-ready HR interview summaries.
    """

    def __init__(self):
        self.risk_keywords = [
            "confused",
            "uncertain",
            "don't know",
            "not sure",
            "no experience"
        ]

    def identify_strengths(self, responses):
        strengths = []

        if responses.get("communication_score", 0) >= 75:
            strengths.append("Strong communication skills")

        if responses.get("confidence_score", 0) >= 75:
            strengths.append("Good confidence during interview")

        if responses.get("relevance_score", 0) >= 75:
            strengths.append("Relevant and focused answers")

        if responses.get("consistency_score", 0) >= 75:
            strengths.append("Consistent responses")

        return strengths

    def identify_weaknesses(self, responses):
        weaknesses = []

        if responses.get("communication_score", 0) < 60:
            weaknesses.append("Communication needs improvement")

        if responses.get("confidence_score", 0) < 60:
            weaknesses.append("Confidence level needs improvement")

        if responses.get("relevance_score", 0) < 60:
            weaknesses.append("Some answers were not sufficiently relevant")

        return weaknesses

    def identify_cultural_fit(self, responses):
        indicators = []

        teamwork = responses.get("teamwork", "").lower()
        adaptability = responses.get("adaptability", "").lower()

        if teamwork:
            if any(
                word in teamwork
                for word in ["team", "collaborate", "support"]
            ):
                indicators.append("Shows teamwork orientation")

        if adaptability:
            if any(
                word in adaptability
                for word in ["adapt", "learn", "flexible"]
            ):
                indicators.append("Shows adaptability")

        return indicators

    def identify_risks(self, responses):
        risks = []

        for answer in responses.get("answers", []):
            answer_lower = answer.lower()

            for keyword in self.risk_keywords:
                if keyword in answer_lower:
                    risks.append(
                        f"Potential risk indicator detected: {keyword}"
                    )

        if responses.get("consistency_score", 100) < 60:
            risks.append("Low consistency score")

        return list(dict.fromkeys(risks))

    def identify_inconsistencies(self, responses):
        inconsistencies = []

        if responses.get("consistency_score", 100) < 60:
            inconsistencies.append(
                "Potential inconsistency detected in interview responses"
            )

        return inconsistencies

    def calculate_overall_score(self, responses):
        scores = [
            responses.get("relevance_score", 0),
            responses.get("communication_score", 0),
            responses.get("confidence_score", 0),
            responses.get("consistency_score", 0)
        ]

        return round(sum(scores) / len(scores), 2)

    def generate_natural_summary(
        self,
        strengths,
        weaknesses,
        cultural_fit,
        risks,
        overall_score
    ):
        summary = (
            f"The candidate achieved an overall HR interview score "
            f"of {overall_score}/100. "
        )

        if strengths:
            summary += (
                "Key strengths include "
                + ", ".join(strengths)
                + ". "
            )

        if weaknesses:
            summary += (
                "Areas requiring attention include "
                + ", ".join(weaknesses)
                + ". "
            )

        if cultural_fit:
            summary += (
                "Cultural fit indicators include "
                + ", ".join(cultural_fit)
                + ". "
            )

        if risks:
            summary += (
                "The interview also contains the following risk indicators: "
                + "; ".join(risks)
                + "."
            )

        return summary.strip()

    def generate_report(self, candidate_id, responses):

        strengths = self.identify_strengths(responses)
        weaknesses = self.identify_weaknesses(responses)
        cultural_fit = self.identify_cultural_fit(responses)
        risks = self.identify_risks(responses)
        inconsistencies = self.identify_inconsistencies(responses)

        overall_score = self.calculate_overall_score(responses)

        summary = self.generate_natural_summary(
            strengths,
            weaknesses,
            cultural_fit,
            risks,
            overall_score
        )

        return {
            "candidate_id": candidate_id,
            "overall_hr_score": overall_score,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "cultural_fit_indicators": cultural_fit,
            "risk_flags": risks,
            "inconsistencies": inconsistencies,
            "summary": summary
        }