class InterviewFlow:

    PHASES = [
        "introduction",
        "core_hr_questions",
        "role_based_evaluation",
        "closing"
    ]

    def __init__(self):

        self.current_phase_index = 0

    def current_phase(self):

        return self.PHASES[
            self.current_phase_index
        ]

    def move_next(self):

        if self.current_phase_index < len(self.PHASES) - 1:

            self.current_phase_index += 1

        return self.current_phase()

    def is_completed(self):

        return (
            self.current_phase_index
            == len(self.PHASES) - 1
        )

    def get_flow(self):

        return {
            "phases": self.PHASES,
            "current_phase": self.current_phase(),
            "phase_number": self.current_phase_index + 1
        }