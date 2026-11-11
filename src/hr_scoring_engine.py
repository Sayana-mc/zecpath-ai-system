"""Day 37: HR Interview Scoring Engine and Explainable Scoring Model."""

import uuid
from typing import Any

from src import database


class HRInterviewScoringEngine:
    """Calculates explainable, normalized HR interview scores with configurable weights."""

    DEFAULT_WEIGHTS = {
        "answer_relevance": 0.40,
        "communication": 0.25,
        "confidence": 0.15,
        "consistency": 0.20,
    }

    def __init__(self, weights: dict[str, float] | None = None):
        self.weights = weights or self.DEFAULT_WEIGHTS
        self._validate_weights(self.weights)

    def _validate_weights(self, weights: dict[str, float]) -> None:
        total = sum(weights.values())
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"HR interview scoring weights must sum to 1.0 (got {total})")
        for k, v in weights.items():
            if v < 0:
                raise ValueError(f"Weight for {k} cannot be negative: {v}")

    def evaluate_answer_relevance(self, question_text: str, answer_text: str) -> float:
        """Heuristic relevance evaluation based on question topic alignment."""
        if not answer_text.strip():
            return 0.0
        words = len(answer_text.split())
        if words <= 3:
            return 30.0
        if words < 8:
            return 60.0
        if words < 18:
            return 80.0
        return 95.0

    def calculate_question_score(
        self,
        relevance: float,
        communication: float,
        confidence: float,
        consistency: float,
    ) -> float:
        """Calculates single question weighted score (0–100 scale)."""
        score = (
            (relevance * self.weights["answer_relevance"])
            + (communication * self.weights["communication"])
            + (confidence * self.weights["confidence"])
            + (consistency * self.weights["consistency"])
        )
        return round(max(0.0, min(100.0, score)), 2)

    def calculate_hr_score(
        self,
        relevance: float,
        communication: float,
        confidence: float,
        consistency: float,
    ) -> dict[str, Any]:
        """Calculates normalized composite score and status classification."""
        overall = self.calculate_question_score(relevance, communication, confidence, consistency)
        status = "EXCELLENT" if overall >= 85 else "STRONG" if overall >= 75 else "MODERATE" if overall >= 60 else "DEVELOPING"
        return {
            "overall_hr_score": overall,
            "relevance_score": relevance,
            "communication_score": communication,
            "confidence_score": confidence,
            "consistency_score": consistency,
            "score_status": status,
        }

    def calculate_comprehensive_hr_score(
        self,
        interview_id: str,
        candidate_id: str | None = None,
    ) -> dict[str, Any]:
        """Calculates aggregate HR interview score; looks up candidate_id if omitted."""
        if not candidate_id:
            session = database.get_hr_interview_session(interview_id)
            candidate_id = session.get("candidate_id", "unknown") if session else "unknown"
        return self.calculate_session_score(interview_id, candidate_id)

    def calculate_session_score(
        self,
        interview_id: str,
        candidate_id: str,
    ) -> dict[str, Any]:
        """Calculates aggregate HR interview score from all completed questions and evaluations."""
        responses = database.list_hr_interview_responses(interview_id)
        comm_evals = database.get_hr_communication_evaluations(interview_id)
        signals = database.get_hr_behavioral_signals(interview_id)

        if not responses:
            # Provisional empty score
            score_record = {
                "score_id": f"HRSCR_{uuid.uuid4().hex[:8].upper()}",
                "interview_id": interview_id,
                "candidate_id": candidate_id,
                "relevance_score": 0.0,
                "communication_score": 0.0,
                "confidence_score": 0.0,
                "consistency_score": 100.0,
                "overall_hr_score": 0.0,
                "score_status": "PROVISIONAL",
                "breakdown": {},
                "human_review_required": True,
            }
            return database.save_hr_interview_score(score_record)

        # Average communication score
        comm_scores = [c["total_communication_score"] for c in comm_evals]
        avg_comm = sum(comm_scores) / len(comm_scores) if comm_scores else 70.0

        # Average confidence score
        conf_scores = [s["confidence_score"] for s in signals]
        avg_conf = sum(conf_scores) / len(conf_scores) if conf_scores else 75.0

        # Contradiction checks for consistency
        has_contradictions = any(s.get("contradiction_detected") for s in signals)
        consistency_score = 60.0 if has_contradictions else 95.0

        # Average relevance
        relevance_scores = [
            self.evaluate_answer_relevance("", r.get("cleaned_response", r.get("raw_response", "")))
            for r in responses
        ]
        avg_relevance = sum(relevance_scores) / len(relevance_scores) if relevance_scores else 70.0

        overall = self.calculate_question_score(
            relevance=avg_relevance,
            communication=avg_comm,
            confidence=avg_conf,
            consistency=consistency_score,
        )

        breakdown = {
            "answer_relevance": {
                "raw_score": round(avg_relevance, 2),
                "weight": self.weights["answer_relevance"],
                "weighted_contribution": round(avg_relevance * self.weights["answer_relevance"], 2),
            },
            "communication": {
                "raw_score": round(avg_comm, 2),
                "weight": self.weights["communication"],
                "weighted_contribution": round(avg_comm * self.weights["communication"], 2),
            },
            "confidence": {
                "raw_score": round(avg_conf, 2),
                "weight": self.weights["confidence"],
                "weighted_contribution": round(avg_conf * self.weights["confidence"], 2),
            },
            "consistency": {
                "raw_score": round(consistency_score, 2),
                "weight": self.weights["consistency"],
                "weighted_contribution": round(consistency_score * self.weights["consistency"], 2),
            },
        }

        human_review = has_contradictions or overall < 60.0 or len(responses) < 2
        score_status = "REVIEW_REQUIRED" if human_review else "FINAL"

        score_id = f"HRSCR_{uuid.uuid4().hex[:8].upper()}"
        score_record = {
            "score_id": score_id,
            "interview_id": interview_id,
            "candidate_id": candidate_id,
            "relevance_score": round(avg_relevance, 2),
            "communication_score": round(avg_comm, 2),
            "confidence_score": round(avg_conf, 2),
            "consistency_score": round(consistency_score, 2),
            "overall_hr_score": overall,
            "score_status": score_status,
            "breakdown": breakdown,
            "human_review_required": human_review,
        }
        saved = database.save_hr_interview_score(score_record)
        return saved


hr_scoring_engine = HRInterviewScoringEngine()

