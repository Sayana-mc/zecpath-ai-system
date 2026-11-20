"""Day 54: Optimization, Accuracy Analysis, Intent Refinement & Inconsistency Detection."""

import json
import time
from pathlib import Path
from typing import Any

try:
    from . import database
except ImportError:
    from src import database


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
                "matches": 0,
                "accuracy": 0.0,
                "precision": 0.0,
                "recall": 0.0,
                "f1_score": 0.0,
                "confusion_matrix": {"tp": 0, "fp": 0, "tn": 0, "fn": 0},
                "false_positive_ids": [],
                "false_negative_ids": [],
            }

        tp = 0
        fp = 0
        tn = 0
        fn = 0
        matches = 0
        fp_ids: list[str] = []
        fn_ids: list[str] = []

        for idx, c in enumerate(cases):
            cid = str(c.get("id") or f"case_{idx+1}")
            score = float(c.get("score", 0.0))
            if "ground_truth" in c:
                ground_truth = str(c["ground_truth"]).upper()
            else:
                ground_truth = "SELECTED" if c.get("ground_truth_suitable") else "REJECTED"

            if score >= strong_threshold:
                predicted = "SELECTED"
            elif score >= potential_threshold:
                predicted = "HOLD_REVIEW"
            else:
                predicted = "REJECTED"

            if predicted == ground_truth:
                matches += 1

            is_gt_positive = ground_truth == "SELECTED"
            is_pred_positive = predicted == "SELECTED"

            if is_pred_positive and is_gt_positive:
                tp += 1
            elif is_pred_positive and not is_gt_positive:
                fp += 1
                fp_ids.append(cid)
            elif not is_pred_positive and is_gt_positive:
                fn += 1
                fn_ids.append(cid)
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
            "false_positive_ids": fp_ids,
            "false_negative_ids": fn_ids,
        }

    @staticmethod
    def detect_score_contradictions(
        round_scores: dict[str, float | None],
        gap_threshold: float = 35.0,
    ) -> list[str]:
        """Flags contradictory scores between resume claims and practical evaluation."""
        contradictions = []
        valid_rounds = {k: float(v) for k, v in round_scores.items() if v is not None}

        if "ats" in valid_rounds and "technical_interview" in valid_rounds:
            gap = abs(valid_rounds["ats"] - valid_rounds["technical_interview"])
            if gap >= gap_threshold:
                contradictions.append(
                    f"Substantial contradiction ({gap:.1f} pts) between resume ATS ({valid_rounds['ats']}) "
                    f"and Technical Interview ({valid_rounds['technical_interview']})."
                )

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

    @staticmethod
    def load_synthetic_validation_dataset() -> dict[str, Any]:
        root = Path(__file__).resolve().parents[1]
        ds_path = root / "day54_optimization_refinement" / "data" / "labelled_evaluations.json"
        if ds_path.exists():
            return json.loads(ds_path.read_text(encoding="utf-8"))
        return {
            "dataset_name": "synthetic_fallback_v1",
            "description": "Synthetic ground-truth demo examples.",
            "examples": [],
        }

    def run_full_optimization_analysis(
        self,
        strong_threshold: float = 80.0,
        potential_threshold: float = 60.0,
        actor_id: str = "system",
        tenant_id: str | None = None,
        save_to_db: bool = True,
    ) -> dict[str, Any]:
        dataset = self.load_synthetic_validation_dataset()
        raw_examples = dataset.get("examples", [])

        # Normalize binary ground_truth_suitable -> 3-class ground_truth for realistic evaluation
        eval_cases: list[dict[str, Any]] = []
        detailed_cases: list[dict[str, Any]] = []
        for item in raw_examples:
            score = float(item.get("score", 0.0))
            suitable = bool(item.get("ground_truth_suitable"))
            completed = int(item.get("completed_rounds", 5))
            r_scores = item.get("round_scores") or []
            gap = (max(r_scores) - min(r_scores)) if r_scores else 0.0
            if not suitable and score < potential_threshold:
                gt = "REJECTED"
            elif suitable and completed >= 3 and gap < 35.0 and score >= strong_threshold:
                gt = "SELECTED"
            else:
                gt = "HOLD_REVIEW"

            # Model prediction using refined rules (missing rounds / contradiction -> HOLD_REVIEW)
            if completed < 3 or gap >= 35.0:
                model_pred = "HOLD_REVIEW"
            elif score >= strong_threshold:
                model_pred = "SELECTED"
            elif score >= potential_threshold:
                model_pred = "HOLD_REVIEW"
            else:
                model_pred = "REJECTED"

            eval_cases.append({"id": item["id"], "score": score, "ground_truth": gt})
            detailed_cases.append({
                "id": item["id"],
                "score": score,
                "completed_rounds": completed,
                "round_score_gap": round(gap, 2),
                "synthetic_ground_truth": gt,
                "baseline_threshold_prediction": "SELECTED" if score >= strong_threshold else ("HOLD_REVIEW" if score >= potential_threshold else "REJECTED"),
                "refined_model_prediction": model_pred,
            })

        baseline_metrics = self.analyze_threshold_accuracy(
            eval_cases, strong_threshold=strong_threshold, potential_threshold=potential_threshold
        )

        # Threshold sweep comparison (50..90 step 10)
        sweep = []
        for t in (50.0, 60.0, 70.0, 80.0, 85.0, 90.0):
            m = self.analyze_threshold_accuracy(eval_cases, strong_threshold=t, potential_threshold=min(t - 5.0, potential_threshold))
            sweep.append({
                "threshold": t,
                "accuracy": m["accuracy"],
                "precision": m["precision"],
                "recall": m["recall"],
                "f1_score": m["f1_score"],
                "fp": m["confusion_matrix"]["fp"],
                "fn": m["confusion_matrix"]["fn"],
            })

        # Measure real processing latencies
        t0 = time.perf_counter()
        for c in detailed_cases:
            self.detect_score_contradictions({"ats": c["score"], "technical_interview": max(0.0, c["score"] - c["round_score_gap"])})
            self.refine_candidate_intent("Explain candidate role fit and architecture", "explain", 0.9)
        synth_ms = (time.perf_counter() - t0) * 1000.0

        db_t0 = time.perf_counter()
        all_evals = database.list_all_cross_round_evaluations(tenant_id=tenant_id, limit=200)
        all_recs = database.list_final_recommendations()
        db_ms = (time.perf_counter() - db_t0) * 1000.0

        decision_dist: dict[str, int] = {"SELECTED": 0, "HOLD_REVIEW": 0, "REJECTED": 0}
        pending_review_count = 0
        for rec in all_recs:
            d = rec.get("decision", "HOLD_REVIEW")
            decision_dist[d] = decision_dist.get(d, 0) + 1
            if rec.get("recruiter_decision") == "PENDING_REVIEW":
                pending_review_count += 1

        missing_stage_eval_count = sum(1 for e in all_evals if e.get("missing_rounds"))

        benchmark = {
            "dataset_eval_ms": round(synth_ms, 3),
            "db_query_ms": round(db_ms, 3),
            "avg_per_candidate_ms": round(synth_ms / max(1, len(detailed_cases)), 4),
            "measured_at": database._now(),
        }

        previous_runs = database.list_optimization_runs(limit=5)
        saved_run = None
        if save_to_db:
            saved_run = database.save_optimization_run(
                dataset_name=dataset.get("dataset_name", "day54_synthetic_validation_v1"),
                strong_threshold=strong_threshold,
                potential_threshold=potential_threshold,
                metrics=baseline_metrics,
                benchmark=benchmark,
                created_by=actor_id,
            )

        return {
            "run_id": saved_run["run_id"] if saved_run else None,
            "dataset_name": dataset.get("dataset_name", "day54_synthetic_validation_v1"),
            "dataset_note": "Synthetic validation dataset only; does not prove real-world hiring accuracy.",
            "strong_threshold": strong_threshold,
            "potential_threshold": potential_threshold,
            "metrics": baseline_metrics,
            "threshold_comparisons": sweep,
            "cases": detailed_cases,
            "live_system_analytics": {
                "total_cross_round_evaluations": len(all_evals),
                "total_recommendations": len(all_recs),
                "decision_distribution": decision_dist,
                "evaluations_with_missing_stages": missing_stage_eval_count,
                "pending_recruiter_reviews": pending_review_count,
            },
            "benchmark": benchmark,
            "previous_runs": previous_runs,
        }


optimization_engine = OptimizationEngine()
