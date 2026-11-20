"""Day 41 & 51 Unified Cross-Round Aggregation & Scoring Engine with Day 42 Anomaly Detection."""

import hashlib
import json
import uuid
from datetime import datetime, timezone
from typing import Any, Mapping

try:
    from . import database
except ImportError:
    from src import database


STAGE_KEYS = ("ats", "screening", "hr_interview", "technical_interview", "machine_test")
VALID_STAGE_STATUSES = {"NOT_STARTED", "PENDING", "NOT_APPLICABLE", "COMPLETED"}

ROLE_ROUND_WEIGHTS: dict[str, dict[str, float]] = {
    "software_engineer": {
        "ats": 10.0,
        "screening": 10.0,
        "hr_interview": 10.0,
        "technical_interview": 30.0,
        "machine_test": 40.0,
    },
    "python_developer": {
        "ats": 10.0,
        "screening": 10.0,
        "hr_interview": 15.0,
        "technical_interview": 35.0,
        "machine_test": 30.0,
    },
    "senior_python_developer": {
        "ats": 10.0,
        "screening": 10.0,
        "hr_interview": 15.0,
        "technical_interview": 35.0,
        "machine_test": 30.0,
    },
    "junior_python_developer": {
        "ats": 10.0,
        "screening": 10.0,
        "hr_interview": 15.0,
        "technical_interview": 35.0,
        "machine_test": 30.0,
    },
    "data_scientist": {
        "ats": 10.0,
        "screening": 15.0,
        "hr_interview": 15.0,
        "technical_interview": 25.0,
        "machine_test": 35.0,
    },
    "data_analyst": {
        "ats": 15.0,
        "screening": 15.0,
        "hr_interview": 20.0,
        "technical_interview": 25.0,
        "machine_test": 25.0,
    },
    "data_analyst_&_bi_specialist": {
        "ats": 15.0,
        "screening": 15.0,
        "hr_interview": 20.0,
        "technical_interview": 25.0,
        "machine_test": 25.0,
    },
    "mern_developer": {
        "ats": 10.0,
        "screening": 10.0,
        "hr_interview": 15.0,
        "technical_interview": 35.0,
        "machine_test": 30.0,
    },
    "mern_stack_developer": {
        "ats": 10.0,
        "screening": 10.0,
        "hr_interview": 15.0,
        "technical_interview": 35.0,
        "machine_test": 30.0,
    },
    "devops_engineer": {
        "ats": 10.0,
        "screening": 15.0,
        "hr_interview": 15.0,
        "technical_interview": 35.0,
        "machine_test": 25.0,
    },
    "default": {
        "ats": 20.0,
        "screening": 20.0,
        "hr_interview": 20.0,
        "technical_interview": 20.0,
        "machine_test": 20.0,
    },
}


class CrossRoundScoringEngine:
    """Unified cross-round aggregation engine fulfilling both Day 41 and Day 51 specifications."""

    SCORE_VERSION = "day51-v1"

    def __init__(self, role_weights: dict[str, dict[str, float]] | None = None):
        self.role_weights = role_weights or ROLE_ROUND_WEIGHTS

    @staticmethod
    def _clean_role(role: str) -> str:
        return str(role or "default").lower().strip().replace(" ", "_")

    @staticmethod
    def validate_weights(weights: Mapping[str, float]) -> dict[str, float]:
        if set(weights.keys()) != set(STAGE_KEYS):
            raise ValueError(f"Weights must define exactly these 5 stages: {', '.join(STAGE_KEYS)}.")
        cleaned: dict[str, float] = {}
        for k, v in weights.items():
            if isinstance(v, bool) or not isinstance(v, (int, float)) or float(v) < 0:
                raise ValueError(f"Invalid weight for {k}: {v}")
            cleaned[k] = float(v)
        total = sum(cleaned.values())
        if abs(total - 100.0) > 0.01:
            raise ValueError(f"Stage weights must sum to 100.0 (got {total:.2f}).")
        return cleaned

    def get_role_weights(self, role: str) -> dict[str, float]:
        clean_role = self._clean_role(role)
        try:
            persisted = database.get_role_weight_configuration(clean_role)
            if persisted and persisted.get("weights"):
                return {k: float(v) for k, v in persisted["weights"].items()}
        except Exception:
            pass
        return dict(self.role_weights.get(clean_role, self.role_weights["default"]))

    def get_min_required_stages(self, role: str) -> int:
        clean_role = self._clean_role(role)
        try:
            persisted = database.get_role_weight_configuration(clean_role)
            if persisted and persisted.get("min_required_stages") is not None:
                return int(persisted["min_required_stages"])
        except Exception:
            pass
        return 3

    @staticmethod
    def normalize_score(raw_score: float, max_score: float = 100.0, min_score: float = 0.0) -> float:
        """Converts raw score to a normalized 0-100 scale with validation."""
        if max_score <= min_score:
            raise ValueError("Maximum score must exceed minimum score.")
        if raw_score < min_score or raw_score > max_score:
            raise ValueError(f"Raw score {raw_score} is outside range [{min_score}, {max_score}].")
        normalized = ((raw_score - min_score) / (max_score - min_score)) * 100.0
        return round(normalized, 2)

    def detect_anomalies(self, round_scores: Mapping[str, float | None]) -> list[str]:
        """Day 42 Anomaly Detection: flags unusual score discrepancies or outliers across rounds."""
        anomalies = []
        completed = {k: float(v) for k, v in round_scores.items() if v is not None}

        for r_name, score in completed.items():
            if score < 0.0 or score > 100.0:
                anomalies.append(f"Score for {r_name} ({score}) is outside standard bounds [0, 100].")

        if "ats" in completed and "technical_interview" in completed:
            diff = abs(completed["ats"] - completed["technical_interview"])
            if diff >= 45.0:
                anomalies.append(
                    f"Discrepancy: Substantial divergence ({diff:.1f} pts) between resume ATS ({completed['ats']}) "
                    f"and Technical Interview ({completed['technical_interview']})."
                )

        if "technical_interview" in completed and "machine_test" in completed:
            t_diff = abs(completed["technical_interview"] - completed["machine_test"])
            if t_diff >= 40.0:
                anomalies.append(
                    f"Discrepancy: Noticeable divergence ({t_diff:.1f} pts) between Technical Interview and Machine Test."
                )

        return anomalies

    def collect_candidate_stage_data(self, candidate_id: str) -> dict[str, Any]:
        """Reads real persisted evaluation records across all 5 stages for a candidate."""
        cand = database.get_candidate(candidate_id)
        if not cand:
            raise ValueError(f"Candidate {candidate_id} not found.")

        stage_scores: dict[str, float | None] = {k: None for k in STAGE_KEYS}
        stage_status: dict[str, str] = {k: "NOT_STARTED" for k in STAGE_KEYS}
        source_refs: dict[str, str | None] = {k: None for k in STAGE_KEYS}

        # 1. ATS
        if cand.get("score") is not None:
            stage_scores["ats"] = round(float(cand["score"]), 2)
            stage_status["ats"] = "COMPLETED"
            source_refs["ats"] = cand["candidate_id"]

        # 2. Screening
        screening_sessions = database.list_screening_sessions(candidate_id)
        if screening_sessions:
            s_sess = screening_sessions[0]
            source_refs["screening"] = s_sess["session_id"]
            agg = database.get_screening_aggregate_score(s_sess["session_id"])
            reports = database.list_screening_reports_full(s_sess["session_id"])
            if agg and agg.get("overall_score") is not None:
                stage_scores["screening"] = round(float(agg["overall_score"]), 2)
                stage_status["screening"] = "COMPLETED"
            elif reports:
                scr_val = reports[0].get("report_json", {}).get("overall_score")
                if scr_val is not None:
                    stage_scores["screening"] = round(float(scr_val), 2)
                    stage_status["screening"] = "COMPLETED"
            else:
                stage_status["screening"] = "PENDING"

        # 3. HR Interview
        hr_sessions = database.list_hr_interview_sessions(candidate_id=candidate_id)
        if hr_sessions:
            hr_sess = hr_sessions[0]
            source_refs["hr_interview"] = hr_sess["interview_id"]
            hr_sc = database.get_hr_interview_score(hr_sess["interview_id"])
            if hr_sc and hr_sc.get("overall_hr_score") is not None:
                stage_scores["hr_interview"] = round(float(hr_sc["overall_hr_score"]), 2)
                stage_status["hr_interview"] = "COMPLETED"
            elif hr_sess.get("status") in {"CREATED", "IN_PROGRESS", "PAUSED"}:
                stage_status["hr_interview"] = "PENDING"

        # 4. Technical Interview
        tech_sessions = database.list_technical_interview_sessions(candidate_id=candidate_id)
        if tech_sessions:
            t_sess = tech_sessions[0]
            source_refs["technical_interview"] = t_sess["session_id"]
            if t_sess.get("status") == "COMPLETED" and t_sess.get("overall_score") is not None:
                stage_scores["technical_interview"] = round(float(t_sess["overall_score"]), 2)
                stage_status["technical_interview"] = "COMPLETED"
            else:
                responses = database.list_technical_interview_responses(t_sess["session_id"])
                if t_sess.get("status") == "COMPLETED" and responses:
                    avg = sum(float(r["score"]) for r in responses) / len(responses)
                    stage_scores["technical_interview"] = round(avg, 2)
                    stage_status["technical_interview"] = "COMPLETED"
                else:
                    stage_status["technical_interview"] = "PENDING"

        # 5. Machine Test
        mt_assigns = database.list_machine_test_assignments(candidate_id=candidate_id)
        if mt_assigns:
            m_assign = mt_assigns[0]
            source_refs["machine_test"] = m_assign["assignment_id"]
            subs = database.list_machine_test_submissions(m_assign["assignment_id"])
            if subs and subs[0].get("total_score") is not None:
                stage_scores["machine_test"] = round(float(subs[0]["total_score"]), 2)
                stage_status["machine_test"] = "COMPLETED"
            else:
                stage_status["machine_test"] = "PENDING"

        return {
            "candidate": cand,
            "stage_scores": stage_scores,
            "stage_status": stage_status,
            "source_refs": source_refs,
        }

    def calculate_hiring_fit(
        self,
        candidate_id: str,
        target_role: str,
        round_scores: Mapping[str, float | None],
        session_id: str | None = None,
        opening_id: str = "",
        stage_status: Mapping[str, str] | None = None,
        role_weights: Mapping[str, float] | None = None,
        min_required_stages: int = 1,
        recalculation_reason: str | None = None,
        save_to_db: bool = True,
        force_recalculate: bool = False,
    ) -> dict[str, Any]:
        """Calculates unified hiring fit % with exclude_and_renormalize policy for missing rounds."""
        weights = (
            self.validate_weights(role_weights)
            if role_weights
            else self.get_role_weights(target_role)
        )

        # Build explicit stage_status
        resolved_status: dict[str, str] = {}
        for k in STAGE_KEYS:
            if stage_status and k in stage_status:
                st = str(stage_status[k]).upper()
                if st not in VALID_STAGE_STATUSES:
                    raise ValueError(f"Invalid stage status for {k}: {st}")
                resolved_status[k] = st
            elif k in round_scores and round_scores[k] is not None:
                resolved_status[k] = "COMPLETED"
            else:
                resolved_status[k] = "NOT_STARTED"

        # Validate score ranges without silently treating missing scores as zero
        completed_rounds: dict[str, float] = {}
        for k in STAGE_KEYS:
            val = round_scores.get(k)
            if val is not None:
                if isinstance(val, bool) or not isinstance(val, (int, float)):
                    raise ValueError(f"Score for round {k} must be numeric: {val}")
                f_val = float(val)
                if not (0.0 <= f_val <= 100.0):
                    raise ValueError(f"Score for round {k} is out of range 0-100: {val}")
                if resolved_status[k] != "NOT_APPLICABLE":
                    completed_rounds[k] = round(f_val, 2)
                    resolved_status[k] = "COMPLETED"

        anomalies = self.detect_anomalies(round_scores)
        missing_stages = [k for k in STAGE_KEYS if k not in completed_rounds and resolved_status[k] != "NOT_APPLICABLE"]

        if not completed_rounds:
            return {
                "candidate_id": candidate_id,
                "target_role": target_role,
                "score_version": self.SCORE_VERSION,
                "hiring_fit_score": 0.0,
                "hiring_fit_percentage": 0.0,
                "fit_category": "NOT_RECOMMENDED",
                "completed_rounds_count": 0,
                "completed_stages": 0,
                "total_rounds_expected": len(weights),
                "round_breakdown": {},
                "stage_scores": {k: None for k in STAGE_KEYS},
                "stage_status": resolved_status,
                "normalized_weights": {},
                "missing_stages": missing_stages,
                "anomalies": anomalies,
                "calculation_status": "NO_COMPLETED_ROUNDS",
                "status": "NO_COMPLETED_ROUNDS",
            }

        completed_weight_sum = sum(weights[r] for r in completed_rounds)
        if completed_weight_sum <= 0:
            completed_weight_sum = 100.0

        renormalized_weights: dict[str, float] = {}
        normalized_fractions: dict[str, float] = {}
        weighted_sum = 0.0

        for r_name, score in completed_rounds.items():
            r_pct = (weights[r_name] / completed_weight_sum) * 100.0
            r_frac = weights[r_name] / completed_weight_sum
            renormalized_weights[r_name] = round(r_pct, 2)
            normalized_fractions[r_name] = round(r_frac, 4)
            weighted_sum += score * r_frac

        insufficient = len(completed_rounds) < int(min_required_stages)
        hiring_fit = round(weighted_sum, 2) if not insufficient else 0.0
        calc_status = "INSUFFICIENT_STAGES" if insufficient else "COMPLETED"

        if insufficient:
            fit_category = "PENDING_REQUIRED_STAGES"
        elif hiring_fit >= 80.0:
            fit_category = "STRONG_FIT"
        elif hiring_fit >= 60.0:
            fit_category = "POTENTIAL_FIT"
        elif hiring_fit >= 50.0:
            fit_category = "LOW_FIT"
        else:
            fit_category = "NOT_RECOMMENDED"

        fp_payload = {
            "candidate_id": candidate_id,
            "target_role": self._clean_role(target_role),
            "stage_scores": completed_rounds,
            "stage_status": resolved_status,
            "weights": weights,
            "min_required_stages": int(min_required_stages),
        }
        input_fingerprint = hashlib.sha256(
            json.dumps(fp_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        ).hexdigest()

        eval_id = f"AGG_{uuid.uuid4().hex[:8].upper()}"
        sess_id = session_id or f"SESS_{uuid.uuid4().hex[:6]}"
        stage_scores_full = {k: completed_rounds.get(k) for k in STAGE_KEYS}

        record = {
            "evaluation_id": eval_id,
            "candidate_id": candidate_id,
            "opening_id": opening_id,
            "session_id": sess_id,
            "target_role": target_role,
            "score_version": self.SCORE_VERSION,
            "ats_score": completed_rounds.get("ats"),
            "screening_score": completed_rounds.get("screening"),
            "hr_interview_score": completed_rounds.get("hr_interview"),
            "technical_interview_score": completed_rounds.get("technical_interview"),
            "machine_test_score": completed_rounds.get("machine_test"),
            "hiring_fit_score": hiring_fit,
            "hiring_fit_percentage": hiring_fit,
            "fit_category": fit_category,
            "weights_used": renormalized_weights,
            "effective_weights": normalized_fractions,
            "normalized_weights": normalized_fractions,
            "configured_weights": weights,
            "round_scores": stage_scores_full,
            "stage_scores": stage_scores_full,
            "stage_status": resolved_status,
            "round_breakdown": completed_rounds,
            "completed_rounds": len(completed_rounds),
            "completed_rounds_count": len(completed_rounds),
            "completed_stages": len(completed_rounds),
            "missing_rounds": missing_stages,
            "missing_stages": missing_stages,
            "anomalies": anomalies,
            "anomalies_detected": anomalies,
            "calculation_status": calc_status,
            "recalculation_reason": recalculation_reason,
            "input_fingerprint": input_fingerprint,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        if save_to_db:
            try:
                if not force_recalculate:
                    existing_fp = database.get_cross_round_evaluation_by_fingerprint(
                        candidate_id, opening_id, input_fingerprint
                    )
                    if existing_fp:
                        existing_fp["duplicate_prevented"] = True
                        return existing_fp
                saved = database.save_cross_round_evaluation(record)
                if isinstance(saved, dict):
                    saved["completed_rounds_count"] = len(completed_rounds)
                    saved["hiring_fit_score"] = saved.get("hiring_fit_percentage", hiring_fit)
                    saved["configured_weights"] = weights
                    saved["duplicate_prevented"] = False
                return saved
            except Exception:
                return record
        return record

    def calculate_unified_fit(
        self,
        round_scores: Mapping[str, Any],
        target_role: str = "software_engineer",
        candidate_id: str = "default_cand",
        role_weights: dict[str, float] | None = None,
        missing_strategy: str = "exclude_and_renormalize",
        stage_status: Mapping[str, str] | None = None,
        min_required_stages: int = 1,
        recalculation_reason: str | None = None,
        save_to_db: bool = True,
        force_recalculate: bool = False,
    ) -> dict[str, Any]:
        """Convenience wrapper for unified 5-round fitting with validation."""
        for k, v in round_scores.items():
            if v is not None:
                if isinstance(v, bool) or not isinstance(v, (int, float)):
                    raise ValueError(f"Score for round {k} must be numeric: {v}")
                if not (0.0 <= float(v) <= 100.0):
                    raise ValueError(f"Score for round {k} is out of range 0-100: {v}")

        res = self.calculate_hiring_fit(
            candidate_id=candidate_id,
            target_role=target_role,
            round_scores=round_scores,
            stage_status=stage_status,
            role_weights=role_weights,
            min_required_stages=min_required_stages,
            recalculation_reason=recalculation_reason,
            save_to_db=save_to_db,
            force_recalculate=force_recalculate,
        )
        weights = role_weights or self.get_role_weights(target_role)
        missing_rounds = [k for k in weights if k not in round_scores or round_scores[k] is None]
        effective_fractions = res.get("normalized_weights") or res.get("effective_weights") or {}
        completed_count = res.get("completed_rounds_count")
        if completed_count is None:
            completed_count = len([k for k, v in round_scores.items() if v is not None and k in weights])

        return {
            "hiring_fit_percentage": res.get("hiring_fit_percentage", 0.0),
            "hiring_fit_score": res.get("hiring_fit_percentage", 0.0),
            "completed_rounds_count": completed_count,
            "missing_rounds": missing_rounds,
            "effective_weights": effective_fractions,
            "normalized_weights": effective_fractions,
            "configured_weights": weights,
            "stage_status": res.get("stage_status", {}),
            "calculation_status": res.get("calculation_status", "COMPLETED"),
            "score_version": res.get("score_version", self.SCORE_VERSION),
            "anomalies": res.get("anomalies", res.get("anomalies_detected", [])),
            "raw_result": res,
        }


cross_round_scoring_engine = CrossRoundScoringEngine()


def calculate_cross_round_score(
    candidate_id: str,
    opening_id: str,
    target_role: str,
    round_scores: Mapping[str, float | None],
    save_to_db: bool = True,
) -> dict[str, Any]:
    engine = CrossRoundScoringEngine()
    res = engine.calculate_unified_fit(
        round_scores=round_scores,
        target_role=target_role,
        candidate_id=candidate_id,
        save_to_db=False,
    )
    fit_score = res.get("hiring_fit_percentage", 0.0)
    if save_to_db:
        database.save_cross_round_evaluation(
            candidate_id=candidate_id,
            opening_id=opening_id,
            target_role=target_role,
            hiring_fit_percentage=fit_score,
            round_scores=round_scores,
            effective_weights=res.get("effective_weights", {}),
            normalized_weights=res.get("normalized_weights", {}),
            stage_status=res.get("stage_status", {}),
            completed_rounds=res.get("completed_rounds_count", len(round_scores)),
            missing_rounds=res.get("missing_rounds", []),
            anomalies=res.get("anomalies", []),
            calculation_status=res.get("calculation_status", "COMPLETED"),
        )
    return res
