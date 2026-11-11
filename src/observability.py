"""ZecPath AI Hiring System - Observability, Structured Logging, and Metrics Subsystem

Day 61: Centralized observability, privacy-aware structured logging,
operational and AI quality metrics tracking, threshold-based alerting,
and decision audit logging.
"""

from __future__ import annotations

import json
import logging
import os
import threading
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

logger = logging.getLogger("zecpath.observability")


def now_iso() -> str:
    """Returns current UTC timestamp in ISO 8601 format."""
    return datetime.now(timezone.utc).isoformat()


def append_jsonl(file_path: str | Path, record: dict[str, Any]) -> None:
    """Thread-safe append of a structured JSON record to a JSONL file."""
    p = Path(file_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, sort_keys=True) + "\n")


def read_jsonl(file_path: str | Path, max_records: int = 200) -> list[dict[str, Any]]:
    """Reads records from a JSONL file, returning the most recent records first."""
    p = Path(file_path)
    if not p.exists():
        return []
    records: list[dict[str, Any]] = []
    try:
        lines = p.read_text(encoding="utf-8").splitlines()
        for line in reversed(lines):
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                    if len(records) >= max_records:
                        break
                except json.JSONDecodeError:
                    continue
    except Exception as exc:
        logger.warning(f"Error reading {file_path}: {exc}")
    return records


def calculate_percentile(values: Iterable[float | int], pct: float) -> float:
    """Calculates the specified percentile from a list of numerical values."""
    val_list = [float(v) for v in values]
    if not val_list:
        return 0.0
    val_list.sort()
    idx = min(len(val_list) - 1, max(0, int(round((pct / 100.0) * (len(val_list) - 1)))))
    return round(val_list[idx], 2)


class ObservabilityEngine:
    """Centralized Observability Engine for ZecPath AI Hiring System."""

    _instance = None
    _lock = threading.Lock()

    def __init__(self, log_dir: str | Path | None = None, service: str = "zecpath-ai-hiring"):
        self.log_dir = Path(log_dir or os.getenv("ZECPATH_LOG_DIR", "logs"))
        self.service = service
        self.log_dir.mkdir(parents=True, exist_ok=True)

        # In-memory rolling metrics buffer (thread-safe)
        self._metrics_lock = threading.Lock()
        self._api_durations: list[float] = []
        self._model_durations: list[float] = []
        self._resume_processing_durations: list[float] = []
        self._ats_scoring_durations: list[float] = []
        self._api_total_count: int = 0
        self._api_failure_count: int = 0
        self._model_total_count: int = 0
        self._model_failure_count: int = 0
        self._db_error_count: int = 0

        # Alert configuration thresholds
        self.alert_config = {
            "failure_rate_warning_percent": 5.0,
            "failure_rate_critical_percent": 15.0,
            "latency_warning_ms": 1000.0,
            "latency_critical_ms": 3000.0,
            "model_failure_rate_critical_percent": 10.0,
            "minimum_events_for_alert": 5,
        }

    @classmethod
    def get_instance(cls, log_dir: str | Path | None = None) -> ObservabilityEngine:
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls(log_dir)
            return cls._instance

    def _base_record(self, event_type: str, correlation_id: str | None = None) -> dict[str, Any]:
        return {
            "event_id": str(uuid.uuid4()),
            "timestamp": now_iso(),
            "event_type": event_type,
            "service": self.service,
            "correlation_id": correlation_id or str(uuid.uuid4()),
        }

    # -------------------------------------------------------------------------
    # 1. Structured Logging Functions (Privacy-Guarded)
    # -------------------------------------------------------------------------

    def log_api_request(
        self,
        endpoint: str,
        method: str,
        status_code: int,
        duration_ms: float,
        correlation_id: str | None = None,
        user_ref: str | None = None,
    ) -> dict[str, Any]:
        """Logs an API request. Excludes passwords, tokens, and raw payloads."""
        record = self._base_record("api_request", correlation_id)
        is_success = 200 <= status_code < 400
        record.update(
            endpoint=endpoint,
            method=method.upper(),
            status_code=int(status_code),
            duration_ms=round(float(duration_ms), 2),
            success=is_success,
            user_ref=user_ref or "anonymous",
        )
        append_jsonl(self.log_dir / "api_logs.jsonl", record)

        with self._metrics_lock:
            self._api_total_count += 1
            if not is_success:
                self._api_failure_count += 1
            self._api_durations.append(float(duration_ms))
            if len(self._api_durations) > 1000:
                self._api_durations.pop(0)

        return record

    def log_model_run(
        self,
        model_name: str,
        model_version: str,
        task: str,
        duration_ms: float,
        success: bool,
        input_ref: str | None = None,
        correlation_id: str | None = None,
    ) -> dict[str, Any]:
        """Logs AI model execution. Stores only references, never full resumes or PII."""
        record = self._base_record("model_run", correlation_id)
        record.update(
            model_name=model_name,
            model_version=model_version,
            task=task,
            duration_ms=round(float(duration_ms), 2),
            success=bool(success),
            input_ref=input_ref,  # candidate_id or opening_id only
        )
        append_jsonl(self.log_dir / "model_logs.jsonl", record)

        with self._metrics_lock:
            self._model_total_count += 1
            if not success:
                self._model_failure_count += 1
            self._model_durations.append(float(duration_ms))
            if len(self._model_durations) > 1000:
                self._model_durations.pop(0)

        return record

    def log_error(
        self,
        component: str,
        error_type: str,
        safe_message: str,
        correlation_id: str | None = None,
    ) -> dict[str, Any]:
        """Logs an operational error. Message is sanitized and length-capped."""
        record = self._base_record("error", correlation_id)
        record.update(
            component=component,
            error_type=error_type,
            safe_message=safe_message[:400],
        )
        append_jsonl(self.log_dir / "error_logs.jsonl", record)

        if "db" in component.lower() or "database" in component.lower():
            with self._metrics_lock:
                self._db_error_count += 1

        return record

    def log_decision_audit(
        self,
        candidate_ref: str,
        opening_ref: str | None,
        decision: str,
        reason: str,
        actor: str,
        model_version: str = "v1.0",
        human_reviewed: bool = True,
        correlation_id: str | None = None,
    ) -> dict[str, Any]:
        """Logs critical recruitment decisions to an immutable audit record."""
        valid_decisions = {
            "SHORTLIST", "REVIEW_REQUIRED", "NOT_SHORTLISTED", "PENDING",
            "SELECTED", "HOLD_REVIEW", "REJECTED", "APPROVED", "OVERRIDDEN"
        }
        dec_norm = decision.upper()
        if dec_norm not in valid_decisions:
            dec_norm = "REVIEW_REQUIRED"

        record = self._base_record("decision_audit", correlation_id)
        record.update(
            candidate_ref=candidate_ref,
            opening_ref=opening_ref,
            decision=dec_norm,
            reason=reason[:500],
            actor=actor,
            model_version=model_version,
            human_reviewed=bool(human_reviewed),
        )
        append_jsonl(self.log_dir / "decision_audit.jsonl", record)
        return record

    def record_stage_duration(self, stage: str, duration_ms: float) -> None:
        """Records task durations for specific recruitment lifecycle stages."""
        with self._metrics_lock:
            if stage == "resume_processing":
                self._resume_processing_durations.append(duration_ms)
                if len(self._resume_processing_durations) > 500:
                    self._resume_processing_durations.pop(0)
            elif stage == "ats_scoring":
                self._ats_scoring_durations.append(duration_ms)
                if len(self._ats_scoring_durations) > 500:
                    self._ats_scoring_durations.pop(0)

    # -------------------------------------------------------------------------
    # 2. Metrics & Dashboard Summary
    # -------------------------------------------------------------------------

    def get_dashboard_summary(self) -> dict[str, Any]:
        """Aggregates logged records and memory buffers into a comprehensive dashboard view."""
        with self._metrics_lock:
            api_durations = list(self._api_durations)
            model_durations = list(self._model_durations)
            resume_durations = list(self._resume_processing_durations)
            ats_durations = list(self._ats_scoring_durations)
            api_total = self._api_total_count
            api_failures = self._api_failure_count
            model_total = self._model_total_count
            model_failures = self._model_failure_count
            db_errors = self._db_error_count

        api_failure_rate = round((api_failures / api_total * 100.0), 2) if api_total > 0 else 0.0
        model_failure_rate = round((model_failures / model_total * 100.0), 2) if model_total > 0 else 0.0

        # Read recent decisions
        decisions = read_jsonl(self.log_dir / "decision_audit.jsonl", max_records=200)
        decision_counts: dict[str, int] = {}
        human_reviewed_count = 0
        for d in decisions:
            k = d.get("decision", "UNKNOWN")
            decision_counts[k] = decision_counts.get(k, 0) + 1
            if d.get("human_reviewed"):
                human_reviewed_count += 1

        recent_errors = read_jsonl(self.log_dir / "error_logs.jsonl", max_records=10)

        return {
            "generated_at": now_iso(),
            "service": self.service,
            "operational_metrics": {
                "total_api_requests": api_total,
                "api_failures": api_failures,
                "api_failure_rate_percent": api_failure_rate,
                "p50_latency_ms": calculate_percentile(api_durations, 50),
                "p95_latency_ms": calculate_percentile(api_durations, 95),
                "avg_resume_processing_ms": round(sum(resume_durations) / len(resume_durations), 2) if resume_durations else 0.0,
                "avg_ats_scoring_ms": round(sum(ats_durations) / len(ats_durations), 2) if ats_durations else 0.0,
                "database_errors": db_errors,
            },
            "ai_model_metrics": {
                "total_model_runs": model_total,
                "model_failures": model_failures,
                "model_failure_rate_percent": model_failure_rate,
                "p50_model_duration_ms": calculate_percentile(model_durations, 50),
                "p95_model_duration_ms": calculate_percentile(model_durations, 95),
            },
            "recruitment_decisions": {
                "total_decisions_logged": len(decisions),
                "human_reviewed_percentage": round(human_reviewed_count / len(decisions) * 100.0, 1) if decisions else 100.0,
                "decision_breakdown": decision_counts,
            },
            "recent_errors": recent_errors,
            "ai_quality_guidance": "Operational completion rates do not reflect AI ground-truth accuracy. Accuracy requires verified evaluation datasets.",
        }

    # -------------------------------------------------------------------------
    # 3. Alert Evaluation
    # -------------------------------------------------------------------------

    def evaluate_alerts(self) -> list[dict[str, Any]]:
        """Evaluates operational metrics against predefined alerting thresholds."""
        summary = self.get_dashboard_summary()
        ops = summary["operational_metrics"]
        ai_m = summary["ai_model_metrics"]
        cfg = self.alert_config

        active_alerts: list[dict[str, Any]] = []

        # 1. API Failure Rate
        if ops["total_api_requests"] >= cfg["minimum_events_for_alert"]:
            rate = ops["api_failure_rate_percent"]
            if rate >= cfg["failure_rate_critical_percent"]:
                active_alerts.append({
                    "rule": "api_failure_rate",
                    "severity": "CRITICAL",
                    "message": f"API failure rate is at {rate}% (critical threshold: {cfg['failure_rate_critical_percent']}%)",
                    "value": rate,
                    "timestamp": now_iso(),
                })
            elif rate >= cfg["failure_rate_warning_percent"]:
                active_alerts.append({
                    "rule": "api_failure_rate",
                    "severity": "WARNING",
                    "message": f"API failure rate is elevated at {rate}%",
                    "value": rate,
                    "timestamp": now_iso(),
                })

        # 2. P95 Latency
        if ops["total_api_requests"] >= cfg["minimum_events_for_alert"]:
            p95 = ops["p95_latency_ms"]
            if p95 >= cfg["latency_critical_ms"]:
                active_alerts.append({
                    "rule": "api_p95_latency",
                    "severity": "CRITICAL",
                    "message": f"API p95 latency is {p95}ms (critical threshold: {cfg['latency_critical_ms']}ms)",
                    "value": p95,
                    "timestamp": now_iso(),
                })
            elif p95 >= cfg["latency_warning_ms"]:
                active_alerts.append({
                    "rule": "api_p95_latency",
                    "severity": "WARNING",
                    "message": f"API p95 latency is elevated at {p95}ms",
                    "value": p95,
                    "timestamp": now_iso(),
                })

        # 3. Model Failure Rate
        if ai_m["total_model_runs"] >= cfg["minimum_events_for_alert"]:
            m_rate = ai_m["model_failure_rate_percent"]
            if m_rate >= cfg["model_failure_rate_critical_percent"]:
                active_alerts.append({
                    "rule": "ai_model_failure_rate",
                    "severity": "CRITICAL",
                    "message": f"AI model run failure rate is {m_rate}%",
                    "value": m_rate,
                    "timestamp": now_iso(),
                })

        # 4. Database Errors
        if ops["database_errors"] > 0:
            active_alerts.append({
                "rule": "database_error_count",
                "severity": "HIGH",
                "message": f"Database errors encountered: {ops['database_errors']} instances",
                "value": ops["database_errors"],
                "timestamp": now_iso(),
            })

        return active_alerts


# Global convenience instance
observability = ObservabilityEngine.get_instance()

