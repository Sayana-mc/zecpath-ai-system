class AptitudeEngine:
    """
    Generates and evaluates aptitude-style questions.

    Categories:
    - logical_reasoning
    - situational_judgment
    - problem_solving
    """

    def __init__(self):
        self.question_bank = [
            {
                "question_id": "APT001",
                "category": "logical_reasoning",
                "question": (
                    "If a project has 10 tasks and 6 are completed, "
                    "how many tasks remain?"
                ),
                "ideal_answer": "4"
            },
            {
                "question_id": "APT002",
                "category": "logical_reasoning",
                "question": (
                    "A team completes 20 tasks in 5 days. "
                    "What is the average number of tasks completed per day?"
                ),
                "ideal_answer": "4"
            },
            {
                "question_id": "APT003",
                "category": "situational_judgment",
                "question": (
                    "You discover an important error just before a deadline. "
                    "What would you do?"
                ),
                "ideal_answer": "identify the error, communicate it, and fix or escalate it"
            }
        ]

    def get_questions(self, category=None):

        if category is None:
            return self.question_bank

        return [
            question
            for question in self.question_bank
            if question["category"] == category
        ]

    def get_question(self, question_id):

        for question in self.question_bank:
            if question["question_id"] == question_id:
                return question

        return None

    def evaluate_answer(self, question_id, answer):

        question = self.get_question(question_id)

        if question is None:
            return {
                "question_id": question_id,
                "status": "unknown_question",
                "score": 0
            }

        if not answer or not answer.strip():
            return {
                "question_id": question_id,
                "status": "missing",
                "score": 0
            }

        return {
            "question_id": question_id,
            "status": "evaluated",
            "answer": answer.strip()
        }