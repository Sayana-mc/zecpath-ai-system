"""Day 47: Technical Skill Scoring Model & Rubric Evaluation."""

import uuid
from typing import Any

try:
    from . import database
except ImportError:
    from src import database


QUESTION_TYPE_WEIGHTS: dict[str, dict[str, float]] = {
    "conceptual": {
        "accuracy": 0.40,
        "depth": 0.30,
        "logical_reasoning": 0.20,
        "real_world_applicability": 0.10,
    },
    "experience_based": {
        "accuracy": 0.25,
        "depth": 0.25,
        "logical_reasoning": 0.20,
        "real_world_applicability": 0.30,
    },
    "scenario_based": {
        "accuracy": 0.25,
        "depth": 0.20,
        "logical_reasoning": 0.30,
        "real_world_applicability": 0.25,
    },
    "system_design": {
        "accuracy": 0.25,
        "depth": 0.25,
        "logical_reasoning": 0.30,
        "real_world_applicability": 0.20,
    },
}


class TechnicalScoringEngine:
    """Evaluates candidate technical responses using multi-factor rubrics."""

    QUESTION_TYPE_WEIGHTS = QUESTION_TYPE_WEIGHTS
    DEFAULT_WEIGHTS = QUESTION_TYPE_WEIGHTS["conceptual"]

    @staticmethod
    def classify_answer_depth(answer: str, scores: dict[str, float]) -> str:
        words = answer.strip().split()
        count = len(words)
        depth = scores.get("depth", 0)
        reasoning = scores.get("logical_reasoning", 0)
        applicability = scores.get("real_world_applicability", 0)

        if count >= 35 and depth >= 4.0 and reasoning >= 3.5 and applicability >= 3.5:
            return "deep"
        if count < 15 or (depth <= 2.0 and reasoning <= 2.0):
            return "shallow"
        return "moderate"

    def evaluate_response_heuristically(self, answer_text: str, question_type: str = "conceptual") -> dict[str, float]:
        """Calculates transparent rubric scores (0-5 scale) based on answer depth, structure, and keywords."""
        words = answer_text.strip().split()
        count = len(words)
        lower = answer_text.lower()

        # Accuracy heuristic
        if count >= 25:
            accuracy = 4.5
        elif count >= 10:
            accuracy = 3.5
        else:
            accuracy = 2.0

        # Depth heuristic
        technical_terms = ["architecture", "scale", "latency", "throughput", "concurrency", "lock", "cache", "async", "schema", "optimize", "buffer", "coroutines", "uvicorn", "threadpool", "celery", "pydantic"]
        matches = sum(1 for t in technical_terms if t in lower)
        depth = min(5.0, 2.5 + (matches * 0.5))

        # Logical reasoning heuristic
        reasoning_connectors = ["because", "therefore", "first", "trade-off", "tradeoff", "hence", "mitigate", "approach", "avoid", "running", "using"]
        r_matches = sum(1 for c in reasoning_connectors if c in lower)
        reasoning = min(5.0, 2.5 + (r_matches * 0.6))

        # Real-world applicability heuristic
        app_terms = ["production", "deployed", "cluster", "metric", "incident", "client", "service", "customer", "team", "worker"]
        a_matches = sum(1 for a in app_terms if a in lower)
        applicability = min(5.0, 2.0 + (a_matches * 0.7))

        if count >= 35 and matches >= 2:
            depth = max(depth, 4.2)
            reasoning = max(reasoning, 4.0)
            applicability = max(applicability, 4.0)
            accuracy = max(accuracy, 4.5)

        return {
            "accuracy": round(accuracy, 2),
            "depth": round(depth, 2),
            "logical_reasoning": round(reasoning, 2),
            "real_world_applicability": round(applicability, 2),
        }

    def score_technical_answer(
        self,
        interview_id: str,
        question_id: str,
        answer_text: str,
        question_type: str = "conceptual",
        custom_scores: dict[str, float] | None = None,
    ) -> dict[str, Any]:
        """Calculates normalized score (0-100) and saves response to database."""
        scores = custom_scores or self.evaluate_response_heuristically(answer_text, question_type)
        depth_class = self.classify_answer_depth(answer_text, scores)

        weights = QUESTION_TYPE_WEIGHTS.get(question_type, QUESTION_TYPE_WEIGHTS["conceptual"])
        weighted_score = sum(scores[param] * weights[param] for param in weights)
        normalized_score = round((weighted_score / 5.0) * 100.0, 2)

        explanation = (
            f"Answer categorized as {depth_class} depth ({len(answer_text.split())} words). "
            f"Accuracy: {scores['accuracy']}/5, Depth: {scores['depth']}/5, "
            f"Reasoning: {scores['logical_reasoning']}/5, Applicability: {scores['real_world_applicability']}/5."
        )

        response_id = f"TRSP_{uuid.uuid4().hex[:8].upper()}"
        record = {
            "response_id": response_id,
            "interview_id": interview_id,
            "question_id": question_id,
            "answer_text": answer_text,
            "accuracy_score": scores["accuracy"],
            "depth_score": scores["depth"],
            "reasoning_score": scores["logical_reasoning"],
            "applicability_score": scores["real_world_applicability"],
            "depth_classification": depth_class,
            "weighted_score": round(weighted_score, 2),
            "normalized_score": normalized_score,
            "explanation": explanation,
        }
        saved = database.save_technical_interview_response(record)
        return saved

    def calculate_technical_session_aggregate(self, interview_id: str) -> dict[str, Any]:
        """Aggregates all question responses for a technical interview."""
        responses = database.list_technical_interview_responses(interview_id)
        if not responses:
            return {
                "interview_id": interview_id,
                "average_score": 0.0,
                "response_count": 0,
                "skill_breakdown": {},
                "status": "NO_RESPONSES",
            }

        total_norm = sum(r["normalized_score"] for r in responses)
        avg_score = round(total_norm / len(responses), 2)

        return {
            "interview_id": interview_id,
            "average_score": avg_score,
            "response_count": len(responses),
            "depth_summary": {
                "deep": sum(1 for r in responses if r["depth_classification"] == "deep"),
                "moderate": sum(1 for r in responses if r["depth_classification"] == "moderate"),
                "shallow": sum(1 for r in responses if r["depth_classification"] == "shallow"),
            },
            "status": "EVALUATED",
        }


technical_scoring_engine = TechnicalScoringEngine()


def score_technical_answer(
    answer_text: str,
    expected_criteria: list[str] | None = None,
    question_type: str = "conceptual",
) -> dict[str, Any]:
    """Convenience functional interface for scoring a single technical answer."""
    param_scores = technical_scoring_engine.evaluate_response_heuristically(
        answer_text, question_type
    )
    weights = technical_scoring_engine.QUESTION_TYPE_WEIGHTS.get(
        question_type, technical_scoring_engine.DEFAULT_WEIGHTS
    )
    weighted_sum = sum(param_scores.get(dim, 2.5) * weight for dim, weight in weights.items())
    score_100 = round((weighted_sum / 5.0) * 100.0, 2)
    depth = TechnicalScoringEngine.classify_answer_depth(answer_text, param_scores)
    return {
        "score": score_100,
        "depth_level": depth,
        "parameter_scores": param_scores,
        "feedback": f"Evaluated as {depth} response with score {score_100:.1f}/100.",
    }

