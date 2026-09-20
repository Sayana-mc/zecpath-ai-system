class InterviewState:

    def __init__(self, candidate_id, role_type, experience_level):

        self.state = {
            "candidate_id": candidate_id,
            "role_type": role_type,
            "experience_level": experience_level,
            "current_phase": "introduction",
            "current_question_id": None,
            "response": None,
            "follow_up_eligible": False,
            "completed_questions": []
        }

    def capture_response(
        self,
        question_id,
        response,
        follow_up_eligible=False
    ):

        self.state["current_question_id"] = question_id
        self.state["response"] = response
        self.state["follow_up_eligible"] = follow_up_eligible

        self.state["completed_questions"].append(
            question_id
        )

    def change_phase(self, phase):

        self.state["current_phase"] = phase

    def get_state(self):

        return self.state