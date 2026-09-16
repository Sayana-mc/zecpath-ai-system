import re


class QuestionScorer:
    """
    Scores an individual screening answer using:
    - Clarity
    - Relevance
    - Completeness
    - Consistency
    """

    def __init__(self, scoring_config):
        self.config = scoring_config

        self.min_score = scoring_config["score_range"]["minimum"]
        self.max_score = scoring_config["score_range"]["maximum"]

        self.weights = {
            name: details["weight"]
            for name, details in scoring_config["parameters"].items()
        }

    def _word_count(self, answer):
        return len(answer.split())

    def score_clarity(self, answer):
        """
        Estimate clarity using answer structure and length.
        """

        if not answer or not answer.strip():
            return 0

        text = answer.strip()
        words = self._word_count(text)

        if words <= 2:
            return 2

        if words <= 5:
            return 3

        if words <= 15:
            return 4

        return 5

    def score_relevance(self, answer, expected_intent):
        """
        Score how closely the answer matches the expected question intent.
        """

        if not answer or not answer.strip():
            return 0

        text = answer.lower()

        if expected_intent == "skills":
            keywords = [
                "python",
                "sql",
                "excel",
                "power bi",
                "tableau",
                "r",
                "java",
                "javascript",
                "tensorflow",
                "pytorch",
                "pandas",
                "numpy"
            ]

        elif expected_intent == "experience":
            keywords = [
                "experience",
                "internship",
                "worked",
                "year",
                "years",
                "month",
                "months"
            ]

        elif expected_intent == "availability":
            keywords = [
                "join",
                "available",
                "immediately",
                "notice",
                "days",
                "weeks"
            ]

        elif expected_intent == "salary_expectation":
            keywords = [
                "salary",
                "lpa",
                "lakh",
                "inr",
                "expecting"
            ]

        else:
            keywords = []

        if not keywords:
            return 3

        matches = sum(
            1
            for keyword in keywords
            if keyword in text
        )

        if matches == 0:
            return 1

        if matches == 1:
            return 3

        return 5

    def score_completeness(self, answer, expected_intent):
        """
        Estimate whether the answer contains enough information.
        """

        if not answer or not answer.strip():
            return 0

        words = self._word_count(answer)

        if words <= 2:
            return 1

        if words <= 5:
            return 3

        text = answer.lower()

        if expected_intent == "skills":
            if "," in answer or "and" in text:
                return 5

            return 4

        if expected_intent == "experience":
            if re.search(
                r"\d+(?:\.\d+)?\s*(year|years|month|months)",
                text
            ):
                return 5

            if re.search(
                r"\b(one|two|three|four|five|six|seven|eight|nine|ten)\s+(year|years|month|months)\b",
                text
            ):
                return 5

            return 4

        if expected_intent == "availability":
            return 5 if (
                "immediately" in text
                or "notice" in text
            ) else 3

        if expected_intent == "salary_expectation":
            return 5 if (
                re.search(
                    r"\d+(?:\.\d+)?\s*(lpa|lakh|lakhs)",
                    text
                )
                or "inr" in text
            ) else 3

        return 4

    def score_consistency(
        self,
        answer,
        previous_information,
        expected_intent
    ):
        """
        Compare extracted answer information with previously available
        candidate information.
        """

        if not answer or not answer.strip():
            return 0

        text = answer.lower()

        if not previous_information:
            return 3

        if expected_intent == "skills":

            previous_skills = previous_information.get(
                "skills",
                []
            )

            if not previous_skills:
                return 3

            matches = sum(
                1
                for skill in previous_skills
                if skill.lower() in text
            )

            if matches == 0:
                return 1

            if matches < len(previous_skills):
                return 4

            return 5

        if expected_intent == "experience":

            previous_years = previous_information.get(
                "experience_years"
            )

            if previous_years is None:
                return 3

            # Numeric experience:
            # Example: "I have 1 year of experience."
            numeric_match = re.search(
                r"(\d+(?:\.\d+)?)\s*(year|years)",
                text
            )

            # Word-based experience:
            # Example: "I have one year of experience."
            number_words = {
                "zero": 0,
                "one": 1,
                "two": 2,
                "three": 3,
                "four": 4,
                "five": 5,
                "six": 6,
                "seven": 7,
                "eight": 8,
                "nine": 9,
                "ten": 10
            }

            word_match = re.search(
                r"\b("
                + "|".join(number_words.keys())
                + r")\s*(year|years)\b",
                text
            )

            answer_years = None

            if numeric_match:
                answer_years = float(
                    numeric_match.group(1)
                )

            elif word_match:
                answer_years = float(
                    number_words[
                        word_match.group(1)
                    ]
                )

            if answer_years is None:
                return 3

            if answer_years == float(previous_years):
                return 5

            difference = abs(
                answer_years - float(previous_years)
            )

            if difference <= 0.5:
                return 4

            return 1

        if expected_intent == "availability":

            previous_availability = previous_information.get(
                "availability"
            )

            if not previous_availability:
                return 3

            if previous_availability.lower() in text:
                return 5

            return 2

        if expected_intent == "salary_expectation":

            previous_salary = previous_information.get(
                "salary_lpa"
            )

            if previous_salary is None:
                return 3

            match = re.search(
                r"(\d+(?:\.\d+)?)\s*(lpa|lakh|lakhs)",
                text
            )

            if not match:
                return 3

            answer_salary = float(
                match.group(1)
            )

            if answer_salary == float(previous_salary):
                return 5

            return 2

        return 3

    def calculate_score(
        self,
        answer,
        expected_intent,
        previous_information=None
    ):

        if previous_information is None:
            previous_information = {}

        clarity = self.score_clarity(
            answer
        )

        relevance = self.score_relevance(
            answer,
            expected_intent
        )

        completeness = self.score_completeness(
            answer,
            expected_intent
        )

        consistency = self.score_consistency(
            answer,
            previous_information,
            expected_intent
        )

        parameter_scores = {
            "clarity": clarity,
            "relevance": relevance,
            "completeness": completeness,
            "consistency": consistency
        }

        weighted_score = sum(
            parameter_scores[name]
            * self.weights[name]
            for name in parameter_scores
        )

        normalized_score = (
            weighted_score / self.max_score
        ) * 100

        return {
            "parameter_scores": parameter_scores,
            "weighted_score": round(
                weighted_score,
                2
            ),
            "normalized_score": round(
                normalized_score,
                2
            )
        }