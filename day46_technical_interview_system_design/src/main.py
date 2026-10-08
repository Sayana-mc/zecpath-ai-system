import json
from pathlib import Path

from .interview_blueprint import build_interview_blueprint


BASE_DIR = Path(__file__).resolve().parent.parent


def main():
    candidate_file = BASE_DIR / "data" / "candidate_profile.json"

    with open(candidate_file, "r", encoding="utf-8") as file:
        candidate = json.load(file)

    blueprint = build_interview_blueprint(candidate)

    output_file = BASE_DIR / "output" / "technical_interview_blueprint.json"

    with open(output_file, "w", encoding="utf-8") as file:
        json.dump(blueprint, file, indent=4)

    print("=" * 60)
    print("DAY 46 - TECHNICAL INTERVIEW SYSTEM DESIGN")
    print("=" * 60)

    print(f"Candidate ID       : {blueprint['candidate_id']}")
    print(f"Role               : {blueprint['role']}")
    print(f"Experience         : {blueprint['experience_years']} years")
    print(f"Experience Level   : {blueprint['experience_level']}")
    print(f"Difficulty         : {blueprint['difficulty']}")

    print("\nSkill Domains:")
    for skill in blueprint["skill_domains"]:
        print(f"  - {skill}")

    print("\nQuestion Types:")
    for question_type in blueprint["question_types"]:
        print(f"  - {question_type}")

    print("\nInterview Flow:")
    for state in blueprint["interview_flow"]["interview_flow"]:
        print(f"  {state['state']} -> {state['next']}")

    print("\nOutput:")
    print(output_file)

    print("=" * 60)


if __name__ == "__main__":
    main()