"""Day 46: Technical Interview System Design & Question Management."""

import uuid
from typing import Any

from src import database


ROLE_SKILL_MAPPING: dict[str, list[str]] = {
    "software_engineer": ["Python", "FastAPI", "Data Structures", "SQL", "System Design"],
    "python_developer": ["Python", "FastAPI", "Django", "AsyncIO", "Databases"],
    "mern_developer": ["React", "Node.js", "Express", "MongoDB", "REST APIs"],
    "java_developer": ["Java", "Spring Boot", "OOP Principles", "Microservices", "SQL"],
    "devops_engineer": ["Docker", "Kubernetes", "CI/CD", "AWS", "Linux"],
    "data_analyst": ["SQL", "Python", "Data Cleaning", "Tableau", "Statistics"],
    "data_scientist": ["Python", "Machine Learning", "Statistics", "SQL", "Data Modeling"],
    "default": ["Problem Solving", "Software Architecture", "Clean Code", "APIs"],
}

TECHNICAL_QUESTION_BANK: list[dict[str, Any]] = [
    # Python & Software Engineer
    {
        "question_id": "TQ_PY_01",
        "role": "software_engineer",
        "domain": "Python",
        "question_type": "conceptual",
        "difficulty": "basic",
        "experience_level": "0-2",
        "question_text": "What is the difference between mutable and immutable types in Python, and how does pass-by-assignment behave?",
    },
    {
        "question_id": "TQ_PY_02",
        "role": "software_engineer",
        "domain": "FastAPI",
        "question_type": "experience_based",
        "difficulty": "intermediate",
        "experience_level": "3-5",
        "question_text": "Can you describe a production API you architected using FastAPI or Flask, explaining how you handled authentication and async database sessions?",
    },
    {
        "question_id": "TQ_PY_03",
        "role": "software_engineer",
        "domain": "System Design",
        "question_type": "scenario_based",
        "difficulty": "advanced",
        "experience_level": "5+",
        "question_text": "A high-volume webhook endpoint is receiving 5,000 requests per second with occasional spikes causing database lock contention. How would you redesign the architecture to guarantee zero data loss and low latency?",
    },
    {
        "question_id": "TQ_PY_04",
        "role": "software_engineer",
        "domain": "Databases",
        "question_type": "system_design",
        "difficulty": "advanced",
        "experience_level": "5+",
        "question_text": "How do you evaluate when to introduce Redis caching versus database read replicas for scaling read-heavy query loads?",
    },
    # MERN Developer
    {
        "question_id": "TQ_MERN_01",
        "role": "mern_developer",
        "domain": "React",
        "question_type": "conceptual",
        "difficulty": "basic",
        "experience_level": "0-2",
        "question_text": "What is the difference between state and props in React, and how does the reconciliation algorithm detect virtual DOM changes?",
    },
    {
        "question_id": "TQ_MERN_02",
        "role": "mern_developer",
        "domain": "Node.js",
        "question_type": "experience_based",
        "difficulty": "intermediate",
        "experience_level": "3-5",
        "question_text": "Explain how the Node.js event loop handles non-blocking I/O operations and how you avoid blocking the worker thread.",
    },
    {
        "question_id": "TQ_MERN_03",
        "role": "mern_developer",
        "domain": "System Design",
        "question_type": "scenario_based",
        "difficulty": "advanced",
        "experience_level": "5+",
        "question_text": "How would you design an end-to-end real-time collaborative dashboard using WebSockets, Node.js microservices, and MongoDB sharding?",
    },
    # DevOps
    {
        "question_id": "TQ_DEVOPS_01",
        "role": "devops_engineer",
        "domain": "Docker",
        "question_type": "conceptual",
        "difficulty": "basic",
        "experience_level": "0-2",
        "question_text": "What is the difference between an image layer and a container layer, and how do multi-stage builds optimize Docker image size?",
    },
    {
        "question_id": "TQ_DEVOPS_02",
        "role": "devops_engineer",
        "domain": "Kubernetes",
        "question_type": "scenario_based",
        "difficulty": "intermediate",
        "experience_level": "3-5",
        "question_text": "A container works properly on a local machine but repeatedly fails with CrashLoopBackOff when deployed to a Kubernetes cluster. Detail your troubleshooting workflow.",
    },
    {
        "question_id": "TQ_DEVOPS_03",
        "role": "devops_engineer",
        "domain": "CI/CD",
        "question_type": "experience_based",
        "difficulty": "advanced",
        "experience_level": "5+",
        "question_text": "How do you implement progressive canary deployments and automated rollback policies using GitOps tools such as ArgoCD or Flux?",
    },
]


class TechnicalInterviewStateMachine:
    """Deterministic finite state machine governing technical interview transitions."""

    PHASES = [
        "CREATED",
        "INTRODUCTION",
        "EXPERIENCE",
        "CONCEPTUAL",
        "SCENARIO",
        "CLOSING",
        "COMPLETED",
    ]

    def __init__(self, current_phase: str = "CREATED"):
        self.current_phase = current_phase if current_phase in self.PHASES else "CREATED"

    def transition_to(self, target_phase: str) -> str:
        if target_phase not in self.PHASES:
            raise ValueError(f"Invalid technical interview phase: {target_phase}")
        self.current_phase = target_phase
        return self.current_phase

    def is_completed(self) -> bool:
        return self.current_phase == "COMPLETED"


class TechnicalInterviewEngine:
    """Manages technical interview session initialization, role mapping, and questions."""

    def __init__(self, questions: list[dict[str, Any]] | None = None):
        self.question_bank = questions or TECHNICAL_QUESTION_BANK

    @staticmethod
    def map_experience_level(years: float) -> str:
        if years <= 2.0:
            return "0-2"
        if years <= 5.0:
            return "3-5"
        return "5+"

    @staticmethod
    def map_difficulty(exp_level: str) -> str:
        if exp_level == "0-2":
            return "basic"
        if exp_level == "3-5":
            return "intermediate"
        return "advanced"

    def select_questions(self, role: str, experience_years: float) -> list[dict[str, Any]]:
        exp_level = self.map_experience_level(experience_years)
        role_key = role.lower().replace(" ", "_")

        matched = [
            q for q in self.question_bank
            if q["role"] == role_key or q["role"] == "software_engineer"
        ]
        if not matched:
            matched = [q for q in self.question_bank if q["role"] == "software_engineer"]

        # Ensure progression across question types
        selected: list[dict[str, Any]] = []
        for q_type in ["conceptual", "experience_based", "scenario_based", "system_design"]:
            cand = [q for q in matched if q["question_type"] == q_type]
            if cand:
                selected.append(cand[0])

        if len(selected) < 3:
            selected = matched[:4]

        return selected

    def generate_questions(
        self,
        target_role: str = "software_engineer",
        experience_level: str = "mid",
        skills: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        """Convenience method generating questions with expected criteria."""
        exp_years = 1.0 if "junior" in experience_level.lower() or "0" in experience_level else 4.0 if "mid" in experience_level.lower() else 7.0
        selected = self.select_questions(target_role, exp_years)
        for q in selected:
            if "expected_criteria" not in q:
                q["expected_criteria"] = ["Technical accuracy", "Production consideration", "Architecture trade-offs"]
        return selected

    def create_technical_session(
        self,
        candidate_id: str,
        opening_id: str,
        role: str = "software_engineer",
        experience_years: float = 3.0,
    ) -> dict[str, Any]:
        """Creates technical interview session and seeds role-specific technical questions."""
        exp_level = self.map_experience_level(experience_years)
        difficulty = self.map_difficulty(exp_level)
        interview_id = f"TECH_{uuid.uuid4().hex[:8].upper()}"

        session_record = {
            "interview_id": interview_id,
            "candidate_id": candidate_id,
            "opening_id": opening_id,
            "role": role,
            "experience_years": experience_years,
            "experience_level": exp_level,
            "difficulty": difficulty,
            "status": "CREATED",
            "current_phase": "CREATED",
            "current_question_id": None,
        }
        saved_session = database.create_technical_interview_session(session_record)

        questions = self.select_questions(role, experience_years)
        saved_questions = []
        for idx, q in enumerate(questions, start=1):
            q_rec = {
                "question_id": f"TQ_{uuid.uuid4().hex[:8].upper()}",
                "interview_id": interview_id,
                "domain": q.get("domain", "General Engineering"),
                "question_type": q.get("question_type", "conceptual"),
                "difficulty": q.get("difficulty", difficulty),
                "question_text": q["question_text"],
                "question_order": idx,
            }
            saved_q = database.save_technical_interview_question(q_rec)
            saved_questions.append(saved_q)

        return {
            "session": saved_session,
            "questions": saved_questions,
        }


technical_interview_engine = TechnicalInterviewEngine()
