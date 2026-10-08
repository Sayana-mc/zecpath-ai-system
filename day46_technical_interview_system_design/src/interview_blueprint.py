import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


def load_json(relative_path):
    file_path = BASE_DIR / relative_path

    with open(file_path, "r", encoding="utf-8") as file:
        return json.load(file)


def determine_experience_level(experience_years):
    if experience_years <= 2:
        return "0-2"

    if experience_years <= 5:
        return "3-5"

    return "5+"


def get_role_skills(role):
    role_mapping = load_json("config/role_skill_mapping.json")

    role_data = role_mapping.get(role)

    if not role_data:
        return []

    return role_data["skill_domains"]


def get_experience_config(experience_years):
    experience_level = determine_experience_level(experience_years)

    experience_config = load_json("config/experience_levels.json")

    return {
        "experience_level": experience_level,
        "config": experience_config[experience_level]
    }


def get_question_hierarchy():
    return load_json("config/question_hierarchy.json")


def get_interview_flow():
    return load_json("config/interview_flow.json")


def build_interview_blueprint(candidate):
    role = candidate["role"]
    experience_years = candidate["experience_years"]

    experience_data = get_experience_config(experience_years)

    blueprint = {
        "candidate_id": candidate["candidate_id"],
        "role": role,
        "experience_years": experience_years,
        "experience_level": experience_data["experience_level"],
        "difficulty": experience_data["config"]["level"],
        "skill_domains": get_role_skills(role),
        "question_types": experience_data["config"]["question_types"],
        "question_hierarchy": get_question_hierarchy(),
        "interview_flow": get_interview_flow()
    }

    return blueprint