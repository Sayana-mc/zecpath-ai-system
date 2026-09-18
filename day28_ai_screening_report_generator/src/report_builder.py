class ScreeningReportBuilder:
    """
    Builds a recruiter-friendly AI screening report
    from structured screening and behavioral data.
    """

    def __init__(self, data):
        self.data = data

    def _get_answers(self):
        return self.data.get("answers", [])

    def _get_information(self, intent):
        for answer in self._get_answers():
            if answer.get("intent") == intent:
                return answer.get("extracted_information", {})
        return {}

    def build_key_answers(self):
        key_answers = []

        for answer in self._get_answers():
            intent = answer.get("intent")

            if intent in {
                "skills",
                "experience",
                "availability",
                "salary_expectation"
            }:
                key_answers.append({
                    "question_id": answer.get("question_id"),
                    "question": answer.get("question"),
                    "answer": answer.get("answer"),
                    "intent": intent
                })

        return key_answers

    def build_strengths(self):
        strengths = []

        skills_info = self._get_information("skills")
        skills = skills_info.get("skills", [])

        if skills:
            strengths.append(
                "Candidate confirmed technical skills: "
                + ", ".join(skills)
            )

        experience_info = self._get_information("experience")

        if experience_info:
            experience_years = experience_info.get(
                "experience_years"
            )

            if experience_years is not None:
                strengths.append(
                    f"Candidate reported {experience_years} "
                    "year(s) of experience."
                )

        behavioral = self.data.get(
            "behavioral_analysis",
            {}
        )

        if behavioral.get("sentiment") == "positive":
            strengths.append(
                "Overall response sentiment was positive."
            )

        if behavioral.get("communication_strength"):
            strengths.append(
                "Communication strength: "
                + behavioral["communication_strength"]
            )

        return strengths

    def build_risks(self):
        risks = []

        for answer in self._get_answers():
            status = answer.get("status")

            if status == "vague":
                risks.append(
                    f"{answer.get('question_id')}: "
                    "Candidate provided a vague answer."
                )

            elif status == "off_topic":
                risks.append(
                    f"{answer.get('question_id')}: "
                    "Candidate provided an off-topic answer."
                )

        behavioral = self.data.get(
            "behavioral_analysis",
            {}
        )

        if behavioral.get("contradictions_detected"):
            risks.append(
                "Contradictory information detected."
            )

        if behavioral.get("hesitation_count", 0) > 3:
            risks.append(
                "Multiple hesitation patterns detected."
            )

        return risks

    def build_missing_data(self):
        missing = []

        required_intents = [
            "skills",
            "experience",
            "availability",
            "salary_expectation"
        ]

        available_intents = {
            answer.get("intent")
            for answer in self._get_answers()
        }

        for intent in required_intents:
            if intent not in available_intents:
                missing.append(intent)

        for answer in self._get_answers():
            if answer.get("status") == "vague":
                missing.append(
                    f"{answer.get('question_id')} requires clarification"
                )

        return missing

    def build_highlights(self):
        highlights = {}

        skills_info = self._get_information("skills")
        highlights["skill_confirmations"] = (
            skills_info.get("skills", [])
        )

        availability_info = self._get_information(
            "availability"
        )

        highlights["availability"] = (
            availability_info.get("availability")
        )

        salary_info = self._get_information(
            "salary_expectation"
        )

        highlights["salary_expectation"] = (
            salary_info.get("salary_lpa")
        )

        return highlights

    def build_behavioral_summary(self):
        behavioral = self.data.get(
            "behavioral_analysis",
            {}
        )

        return {
            "communication_strength":
                behavioral.get(
                    "communication_strength"
                ),
            "hesitation_count":
                behavioral.get(
                    "hesitation_count",
                    0
                ),
            "uncertainty_count":
                behavioral.get(
                    "uncertainty_count",
                    0
                ),
            "average_response_length":
                behavioral.get(
                    "average_response_length"
                ),
            "sentiment":
                behavioral.get("sentiment"),
            "contradictions_detected":
                behavioral.get(
                    "contradictions_detected",
                    False
                )
        }

    def build_report(self):

        return {
            "report_metadata": {
                "candidate_id":
                    self.data.get("candidate_id"),
                "candidate_name":
                    self.data.get("candidate_name"),
                "job_id":
                    self.data.get("job_id"),
                "job_title":
                    self.data.get("job_title")
            },

            "screening_summary": {
                "total_score":
                    self.data.get(
                        "screening_score",
                        {}
                    ).get("total_score"),
                "questions_evaluated":
                    self.data.get(
                        "screening_score",
                        {}
                    ).get("questions_evaluated")
            },

            "key_answers":
                self.build_key_answers(),

            "strengths":
                self.build_strengths(),

            "risks":
                self.build_risks(),

            "missing_data":
                self.build_missing_data(),

            "highlights":
                self.build_highlights(),

            "behavioral_summary":
                self.build_behavioral_summary()
        }