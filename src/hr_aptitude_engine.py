"""Day 38: Aptitude, Logical Reasoning, and Situational Judgment Engine."""

import uuid
from typing import Any

from src import database


APTITUDE_QUESTION_BANK = [
    {
        "question_id": "APT_LOGIC_01",
        "category": "logical_reasoning",
        "question": "If a team has 12 development tasks, 4 are high priority, and 3 high-priority tasks are completed on day one, what proportion of high-priority tasks remain?",
        "ideal_answer_rubric": "1 out of 4 high-priority tasks remain (25%). Shows step-by-step arithmetic reasoning.",
        "keywords": ["1", "25%", "one", "one fourth", "remaining"],
    },
    {
        "question_id": "APT_PROBLEM_01",
        "category": "problem_solving",
        "question": "You discover a critical bug in a core service 30 minutes before a planned client release. How do you approach this problem?",
        "ideal_answer_rubric": "Assesses bug severity, communicates with team/stakeholders, considers postponing vs rollback vs hotfix, and implements preventive post-mortem.",
        "keywords": ["assess", "severity", "communicate", "stakeholders", "rollback", "postpone", "hotfix", "prevent"],
    },
    {
        "question_id": "APT_SITUATION_01",
        "category": "situational_judgment",
        "question": "You are assigned two urgent tasks with the same deadline: one blocks an important external client, while the other blocks your internal engineering team. How do you prioritize?",
        "ideal_answer_rubric": "Evaluates client SLA impact vs internal engineering blocker, communicates with manager/leads for trade-off alignment, delegates or stages the tasks.",
        "keywords": ["impact", "client", "team", "communicate", "prioritize", "manager", "delegate", "trade-off"],
    },
    {
        "question_id": "APT_DECISION_01",
        "category": "decision_making",
        "question": "When faced with incomplete technical requirements and an approaching delivery milestone, how do you make decisions?",
        "ideal_answer_rubric": "Clarifies assumptions with product manager, documents risks, proceeds with MVP scope, and maintains transparent status updates.",
        "keywords": ["clarify", "assumptions", "product", "scope", "risks", "document", "mvp"],
    },
]


class HRAptitudeEngine:
    """Manages reasoning-based and situational assessment questions and evaluations."""

    def __init__(self, question_bank: list[dict[str, Any]] | None = None):
        self.question_bank = question_bank or APTITUDE_QUESTION_BANK

    def get_questions(self, category: str | None = None) -> list[dict[str, Any]]:
        if not category:
            return self.question_bank
        return [q for q in self.question_bank if q["category"].lower() == category.lower()]

    def get_aptitude_questions(self, category: str | None = None) -> list[dict[str, Any]]:
        return self.get_questions(category)

    def get_question(self, question_id: str) -> dict[str, Any] | None:
        for q in self.question_bank:
            if q["question_id"] == question_id:
                return q
        return None

    def evaluate_aptitude_answer(
        self,
        question_id: str,
        category: str | None = None,
        candidate_answer: str = "",
    ) -> dict[str, Any]:
        return self.evaluate_reasoning_answer(question_id, candidate_answer)

    def evaluate_reasoning_answer(
        self,
        question_id: str,
        candidate_answer: str,
    ) -> dict[str, Any]:
        """Evaluates logical reasoning or situational answer against rubric dimensions."""
        question = self.get_question(question_id)
        if not candidate_answer or not candidate_answer.strip():
            return {
                "logic_score": 0.0,
                "clarity_score": 0.0,
                "problem_solving_score": 0.0,
                "decision_making_score": 0.0,
                "communication_score": 0.0,
                "overall_score": 0.0,
                "details": {"notes": "Empty response provided."},
            }

        text = candidate_answer.lower()
        words = text.split()

        # Check logic connectors
        logic_connectors = ["because", "therefore", "first", "then", "since", "so", "consequently", "step"]
        logic_matches = sum(1 for c in logic_connectors if c in text)
        if logic_matches >= 3:
            logic_score = 90.0
        elif logic_matches >= 1:
            logic_score = 75.0
        else:
            logic_score = 55.0

        # Check clarity
        if len(words) <= 5:
            clarity_score = 40.0
        elif len(words) <= 15:
            clarity_score = 70.0
        else:
            clarity_score = 88.0

        # Rubric keyword matches if question has them
        rubric_keywords = question.get("keywords", []) if question else []
        keyword_hits = [k for k in rubric_keywords if k in text]
        general_problem_solving = ["matrix", "trade-off", "tradeoff", "impact", "feasibility", "solution", "consensus", "root cause", "investigate", "resolve", "approach", "workshop", "align"]
        general_hits = [g for g in general_problem_solving if g in text]
        hit_ratio = (len(keyword_hits) / len(rubric_keywords)) if rubric_keywords else 0.5
        if general_hits:
            hit_ratio = max(hit_ratio, min(1.0, 0.4 + (len(general_hits) * 0.2)))
        problem_solving_score = min(95.0, 50.0 + (hit_ratio * 45.0))

        # Decision making & communication
        decision_score = 80.0 if any(d in text for d in ["decide", "prioritize", "choose", "plan", "escalate"]) else 65.0
        comm_score = 85.0 if len(words) >= 12 else 60.0

        overall = round(
            (logic_score * 0.30)
            + (problem_solving_score * 0.25)
            + (decision_score * 0.25)
            + (clarity_score * 0.20),
            2,
        )

        return {
            "logic_score": logic_score,
            "clarity_score": clarity_score,
            "problem_solving_score": problem_solving_score,
            "decision_making_score": decision_score,
            "communication_score": comm_score,
            "overall_score": overall,
            "details": {
                "keyword_hits": keyword_hits,
                "logic_connectors_used": logic_matches,
                "word_count": len(words),
            },
        }

    def evaluate_and_save(
        self,
        interview_id: str,
        question_id: str,
        candidate_answer: str,
    ) -> dict[str, Any]:
        """Runs evaluation and persists record to database."""
        question = self.get_question(question_id)
        category = question.get("category", "situational_judgment") if question else "situational_judgment"
        eval_result = self.evaluate_reasoning_answer(question_id, candidate_answer)

        aptitude_id = f"HRAPT_{uuid.uuid4().hex[:8].upper()}"
        aptitude_record = {
            "aptitude_id": aptitude_id,
            "interview_id": interview_id,
            "question_id": question_id,
            "category": category,
            "candidate_answer": candidate_answer,
            "logic_score": eval_result["logic_score"],
            "clarity_score": eval_result["clarity_score"],
            "problem_solving_score": eval_result["problem_solving_score"],
            "decision_making_score": eval_result["decision_making_score"],
            "communication_score": eval_result["communication_score"],
            "overall_score": eval_result["overall_score"],
            "evaluation_details": eval_result["details"],
        }
        saved = database.save_hr_aptitude_evaluation(interview_id, aptitude_record)
        return saved


hr_aptitude_engine = HRAptitudeEngine()

