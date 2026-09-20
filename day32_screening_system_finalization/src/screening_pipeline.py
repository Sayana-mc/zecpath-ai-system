from datetime import datetime


class ScreeningPipeline:

    def __init__(self):
        self.questions = [
            {
                "question_id": "Q001",
                "category": "skills",
                "question": "What technical skills do you have?"
            },
            {
                "question_id": "Q002",
                "category": "experience",
                "question": "Tell me about your experience."
            },
            {
                "question_id": "Q003",
                "category": "availability",
                "question": "When can you join?"
            },
            {
                "question_id": "Q004",
                "category": "salary",
                "question": "What is your salary expectation?"
            }
        ]

    def process_candidate(self, candidate_id, answers):

        processed_answers = []

        for question in self.questions:

            answer = answers.get(
                question["question_id"],
                ""
            )

            if not answer.strip():
                status = "missing"
            else:
                status = "processed"

            processed_answers.append({
                "question_id": question["question_id"],
                "category": question["category"],
                "question": question["question"],
                "answer": answer,
                "status": status
            })

        return {
            "candidate_id": candidate_id,
            "screening_id": f"SCR-{candidate_id}",
            "timestamp": datetime.now().isoformat(),
            "status": "completed",
            "total_questions": len(self.questions),
            "answers": processed_answers
        }