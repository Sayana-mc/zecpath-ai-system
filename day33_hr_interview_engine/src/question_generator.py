from question_bank import QUESTION_BANK


class QuestionGenerator:

    def generate_questions(
        self,
        experience_level="fresher",
        role_type="non_technical"
    ):
        questions = []

        for category, category_questions in QUESTION_BANK.items():

            for item in category_questions:

                experience_match = (
                    item["experience_level"] == "both"
                    or item["experience_level"] == experience_level
                )

                role_match = (
                    item["role_type"] == "both"
                    or item["role_type"] == role_type
                )

                if experience_match and role_match:
                    questions.append(item)

        return questions