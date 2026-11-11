"""Day 58: Candidate AI Coaching, Developmental Feedback & Ethical Guardrails."""

from typing import Any
from src import database


COACHING_DISCLAIMER: str = (
    "Candidate coaching suggestions and practice questions are purely developmental aids. "
    "They do NOT influence hiring decisions, ratings, or candidate status."
)


class CandidateCoachingEngine:
    """Generates post-assessment coaching recommendations, practice problems, and enforces safety guardrails."""

    @staticmethod
    def generate_candidate_coaching(
        candidate_id: str,
        target_role: str = "Software Engineer",
        save_to_db: bool = True,
    ) -> dict[str, Any]:
        """
        Analyzes candidate skill gaps and interview performance to produce
        personalized developmental guidance and practice questions.
        """
        candidate = database.get_candidate(candidate_id)
        if not candidate:
            raise ValueError(f"Candidate {candidate_id} not found.")

        missing_skills = candidate.get("missing_skills") or []
        extracted_skills = candidate.get("extracted_skills") or []

        # Technical interview responses
        tech_sessions = database.list_technical_interview_sessions(candidate_id)
        shallow_topics = []
        if tech_sessions:
            responses = database.list_technical_interview_responses(tech_sessions[0]["session_id"])
            for r in responses:
                if r.get("depth_classification") == "shallow":
                    shallow_topics.append(r.get("question_id", "System Architecture"))

        identified_skill_gaps = list(dict.fromkeys(missing_skills + shallow_topics))
        if not identified_skill_gaps:
            identified_skill_gaps = ["Distributed Caching & Concurrency", "System Scalability Trade-offs"]

        # Preparation advice
        preparation_steps = [
            f"Review architectural concepts and design patterns for: {', '.join(identified_skill_gaps[:3])}.",
            "Practice writing production-ready code with comprehensive error handling and test assertions.",
            "Formulate answers using the STAR method (Situation, Task, Action, Result) with concrete metrics.",
        ]

        # Practice questions
        practice_questions = [
            f"How would you design a fault-tolerant data ingestion pipeline utilizing {identified_skill_gaps[0]}?",
            "Describe a production incident you investigated. What telemetry did you inspect and how did you resolve it?",
            "What architectural trade-offs do you evaluate when choosing between relational indexing and distributed key-value caches?",
        ]

        coaching_payload = {
            "candidate_id": candidate_id,
            "target_role": target_role,
            "identified_skill_gaps": identified_skill_gaps,
            "recommended_preparation": preparation_steps,
            "practice_questions": practice_questions,
            "governance_guardrails": {
                "influences_hiring_status": False,
                "emotion_detection_enabled": False,
                "automatic_rejection_enabled": False,
                "human_recruiter_decision_only": True,
            },
            "disclaimer": COACHING_DISCLAIMER,
        }

        if save_to_db:
            saved = database.save_coaching_record(
                candidate_id=candidate_id,
                target_role=target_role,
                identified_skill_gaps=identified_skill_gaps,
                recommended_preparation=preparation_steps,
                practice_questions=practice_questions,
            )
            coaching_payload["coaching_id"] = saved["coaching_id"]
            coaching_payload["created_at"] = saved["created_at"]

        return coaching_payload


coaching_engine = CandidateCoachingEngine()
generate_candidate_coaching = CandidateCoachingEngine.generate_candidate_coaching

