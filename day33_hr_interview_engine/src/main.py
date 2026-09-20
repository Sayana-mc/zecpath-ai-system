import sys
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]

SRC_DIR = (
    PROJECT_ROOT /
    "day33_hr_interview_engine" /
    "src"
)

sys.path.insert(0, str(SRC_DIR))

from question_generator import QuestionGenerator
from interview_state import InterviewState
from interview_flow import InterviewFlow


def main():

    print("=" * 60)
    print("DAY 33 - HR INTERVIEW ENGINE")
    print("=" * 60)

    candidate_id = "C001"
    experience_level = "fresher"
    role_type = "technical"

    generator = QuestionGenerator()

    questions = generator.generate_questions(
        experience_level=experience_level,
        role_type=role_type
    )

    state = InterviewState(
        candidate_id,
        role_type,
        experience_level
    )

    flow = InterviewFlow()

    state.capture_response(
        "HR001",
        "I am a Data Science and Analytics postgraduate.",
        follow_up_eligible=True
    )

    state.change_phase("core_hr_questions")

    output = {
        "candidate_id": candidate_id,
        "experience_level": experience_level,
        "role_type": role_type,
        "question_bank_count": len(questions),
        "generated_questions": questions,
        "interview_state": state.get_state(),
        "conversation_flow": flow.get_flow()
    }

    output_dir = (
        PROJECT_ROOT /
        "day33_hr_interview_engine" /
        "output"
    )

    output_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    output_file = (
        output_dir /
        "hr_interview_structure.json"
    )

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            output,
            file,
            indent=4
        )

    print()
    print("Candidate ID:", candidate_id)
    print("Experience Level:", experience_level)
    print("Role Type:", role_type)
    print("Questions Generated:", len(questions))
    print("Current Phase:", state.get_state()["current_phase"])
    print("Interview Phases:", flow.PHASES)
    print()
    print("HR Interview Engine Design Completed.")
    print("Output:", output_file)


if __name__ == "__main__":
    main()