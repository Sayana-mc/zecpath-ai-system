"""Day 54: Optimization, Accuracy Analysis, Intent Refinement & Inconsistency Detection."""

from statistics import mean
from typing import Any


class OptimizationEngine:
    """Provides analytical evaluation of scoring accuracy, intent refinement, and contradiction detection."""

    @staticmethod
    def analyze_threshold_accuracy(
        cases: list[dict[str, Any]],
        strong_threshold: float = 80.0,
        potential_threshold: float = 60.0,
    ) -> dict[str, Any]:
        """
        Evaluates system decision accuracy against human-reviewed ground truth labels.
        Labels expected: 'SELECTED', 'HOLD_REVIEW', 'REJECTED'.
        """
        if not cases:
            return {
                "total_cases": 0,
                "accuracy": 0.0,
                "precision": 0.0,
                "recall": 0.0,
                "f1_score": 0.0,
                "confusion_matrix": {"tp": 0, "fp": 0, "tn": 0, "fn": 0},
            }

        tp = 0
        fp = 0
        tn = 0
        fn = 0
        matches = 0

        for c in cases:
            score = float(c.get("score", 0.0))
            ground_truth = str(c.get("ground_truth", "")).upper()

            if score >= strong_threshold:
                predicted = "SELECTED"
            elif score >= potential_threshold:
                predicted = "HOLD_REVIEW"
            else:
                predicted = "REJECTED"

            if predicted == ground_truth:
                matches += 1

            # Binary metrics for SELECTED class
            if predicted == "SELECTED" and ground_truth == "SELECTED":
                tp += 1
            elif predicted == "SELECTED" and ground_truth != "SELECTED":
                fp += 1
            elif predicted != "SELECTED" and ground_truth == "SELECTED":
                fn += 1
            else:
                tn += 1

        accuracy = round(matches / len(cases), 4)
        precision = round(tp / (tp + fp), 4) if (tp + fp) > 0 else 0.0
        recall = round(tp / (tp + fn), 4) if (tp + fn) > 0 else 0.0
        f1 = round((2 * precision * recall) / (precision + recall), 4) if (precision + recall) > 0 else 0.0

        return {
            "total_cases": len(cases),
            "matches": matches,
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1_score": f1,
            "confusion_matrix": {"tp": tp, "fp": fp, "tn": tn, "fn": fn},
        }

    @staticmethod
    def detect_score_contradictions(
        round_scores: dict[str, float | None],
        gap_threshold: float = 35.0,
    ) -> list[str]:
        """Flags contradictory scores between resume claims and practical evaluation."""
        contradictions = []
        valid_rounds = {k: v for k, v in round_scores.items() if v is not None}

        # ATS vs Technical Interview
        if "ats" in valid_rounds and "technical_interview" in valid_rounds:
            gap = abs(valid_rounds["ats"] - valid_rounds["technical_interview"])
            if gap >= gap_threshold:
                contradictions.append(
                    f"Substantial contradiction ({gap:.1f} pts) between resume ATS ({valid_rounds['ats']}) "
                    f"and Technical Interview ({valid_rounds['technical_interview']})."
                )

        # Technical Interview vs Machine Test
        if "technical_interview" in valid_rounds and "machine_test" in valid_rounds:
            gap = abs(valid_rounds["technical_interview"] - valid_rounds["machine_test"])
            if gap >= gap_threshold:
                contradictions.append(
                    f"Noticeable divergence ({gap:.1f} pts) between Technical Interview ({valid_rounds['technical_interview']}) "
                    f"and Machine Test ({valid_rounds['machine_test']})."
                )

        return contradictions

    @staticmethod
    def refine_candidate_intent(
        answer_text: str,
        detected_intent: str | None = None,
        confidence: float = 0.5,
    ) -> dict[str, Any]:
        """
        Refines candidate intent detection, flagging ambiguous or low-confidence responses
        and recommending clarifying follow-up prompts instead of guessing.
        """
        text = answer_text.strip()
        words = text.split()

        if len(words) < 5 or confidence < 0.6 or detected_intent in (None, "unknown", "ambiguous"):
            return {
                "refined_intent": "clarification_needed",
                "confidence": round(confidence, 2),
                "requires_clarification": True,
                "recommended_followup": "Could you elaborate more on your specific approach or experience regarding this question?",
                "status": "AMBIGUOUS",
            }

        return {
            "refined_intent": detected_intent,
            "confidence": round(confidence, 2),
            "requires_clarification": False,
            "recommended_followup": None,
            "status": "CONFIDENT",
        }


optimization_engine = OptimizationEngine()

