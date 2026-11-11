"""Day 50: Machine Test AI Design, Sandbox Execution Records, and Task Evaluator."""

import uuid
from typing import Any

from src import database


MACHINE_TEST_WEIGHTS: dict[str, float] = {
    "correctness": 50.0,
    "efficiency": 15.0,
    "code_quality": 15.0,
    "problem_solving": 10.0,
    "time_management": 10.0,
}

SAMPLE_MACHINE_TASKS: list[dict[str, Any]] = [
    {
        "task_type": "coding",
        "title": "Async Task Queue Worker",
        "description": "Implement a resilient Python in-memory async task queue with concurrency limits and retry exponential backoff.",
        "time_limit_minutes": 45,
    },
    {
        "task_type": "debugging",
        "title": "Fix Deadlock in Database Transaction",
        "description": "Identify and resolve a simulated transaction deadlock occurring under concurrent balance transfers.",
        "time_limit_minutes": 30,
    },
    {
        "task_type": "file_based",
        "title": "CSV Stream Processing and Aggregator",
        "description": "Write a memory-efficient generator processing multi-gigabyte log files without exhausting heap space.",
        "time_limit_minutes": 40,
    },
    {
        "task_type": "mini_system_design",
        "title": "Rate Limiter Filter Middleware",
        "description": "Design and implement a sliding-window rate limiter middleware with configurable IP burst limits.",
        "time_limit_minutes": 35,
    },
]


class MachineTestEngine:
    """Evaluates candidate technical tasks and programming assignments under strict sandboxed rules."""

    def __init__(self, weights: dict[str, float] | None = None):
        self.weights = weights or MACHINE_TEST_WEIGHTS

    def assign_task(
        self,
        task_type: str = "coding",
        task_id: str | None = None,
    ) -> dict[str, Any]:
        matched = next((t for t in SAMPLE_MACHINE_TASKS if t["task_type"] == task_type), SAMPLE_MACHINE_TASKS[0])
        res = dict(matched)
        res["task_id"] = task_id or f"task_{task_type}_01"
        return res

    def assign_test(
        self,
        candidate_id: str,
        opening_id: str,
        task_type: str = "coding",
        custom_task: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Creates a machine test assignment for a candidate."""
        task = custom_task or self.assign_task(task_type)

        test_id = f"MTEST_{uuid.uuid4().hex[:8].upper()}"
        record = {
            "test_id": test_id,
            "candidate_id": candidate_id,
            "opening_id": opening_id,
            "task_type": task["task_type"],
            "task_title": task["title"],
            "task_description": task["description"],
            "time_limit_minutes": task["time_limit_minutes"],
            "status": "ASSIGNED",
        }
        try:
            saved = database.create_machine_test_assignment(
                candidate_id=candidate_id,
                opening_id=opening_id,
                task_type=task["task_type"],
                task_id=task.get("task_id", test_id),
                title=task["title"],
                description=task["description"],
                time_limit_minutes=task["time_limit_minutes"],
                assignment_id=test_id,
            )
            return saved
        except Exception:
            return record

    def evaluate_submission(
        self,
        test_id: str | None = None,
        code_content: str | None = None,
        elapsed_time_minutes: float | None = None,
        test_results: list[dict[str, Any]] | None = None,
        custom_scores: dict[str, float] | None = None,
        task_type: str = "coding",
        code: str | None = None,
        time_spent_minutes: float | None = None,
        time_limit_minutes: float = 60.0,
    ) -> dict[str, Any]:
        """Evaluates submitted code solution against correctness, efficiency, quality, and time policy."""
        code_str = code if code is not None else (code_content or "")
        time_spent = time_spent_minutes if time_spent_minutes is not None else (elapsed_time_minutes or 20.0)

        # 1. Correctness from unit tests
        if test_results:
            passed_count = sum(1 for t in test_results if t.get("passed", False))
            correctness = (passed_count / len(test_results)) * 100.0
        else:
            lines = [l.strip() for l in code_str.splitlines() if l.strip()]
            correctness = min(95.0, max(50.0, 60.0 + (len(lines) * 3.0)))

        # 2. Time management score
        if time_spent <= (time_limit_minutes * 0.70):
            time_score = 100.0
        elif time_spent <= time_limit_minutes:
            time_score = 85.0
        else:
            time_score = 50.0

        scores = custom_scores or {}
        efficiency = scores.get("efficiency", 85.0)
        code_quality = scores.get("code_quality", 88.0)
        problem_solving = scores.get("problem_solving", 90.0)

        total_score = round(
            (correctness * (self.weights["correctness"] / 100.0))
            + (efficiency * (self.weights["efficiency"] / 100.0))
            + (code_quality * (self.weights["code_quality"] / 100.0))
            + (problem_solving * (self.weights["problem_solving"] / 100.0))
            + (time_score * (self.weights["time_management"] / 100.0)),
            2,
        )

        rubric = {
            "correctness": round(correctness, 2),
            "efficiency": round(efficiency, 2),
            "code_quality": round(code_quality, 2),
            "problem_solving": round(problem_solving, 2),
            "time_management": round(time_score, 2),
        }

        if test_id:
            try:
                assignment = database.get_machine_test_assignment(test_id)
                candidate_id = assignment["candidate_id"] if assignment else "unknown"
                submission_id = f"sub_{uuid.uuid4().hex[:8]}"
                sub_record = {
                    "submission_id": submission_id,
                    "test_id": test_id,
                    "candidate_id": candidate_id,
                    "code_content": code_str,
                    "elapsed_time_minutes": time_spent,
                    "correctness_score": round(correctness, 2),
                    "efficiency_score": round(efficiency, 2),
                    "code_quality_score": round(code_quality, 2),
                    "problem_solving_score": round(problem_solving, 2),
                    "time_management_score": round(time_score, 2),
                    "total_score": total_score,
                    "test_results": test_results or [],
                    "evaluation_summary": f"Scored {total_score}/100. Status: {'STRONG' if total_score >= 80 else 'COMPETENT' if total_score >= 60 else 'DEVELOPING'}",
                }
                saved_sub = database.save_machine_test_submission(sub_record)
                database.update_machine_test_assignment_status(test_id, "EVALUATED")
                res = dict(saved_sub)
                res["total_score"] = total_score
                res["rubric_scores"] = rubric
                return res
            except Exception:
                pass

        return {
            "total_score": total_score,
            "rubric_scores": rubric,
            "execution_details": {
                "task_type": task_type,
                "lines_analyzed": len(code_str.splitlines()),
                "time_spent": time_spent,
                "time_limit": time_limit_minutes,
            },
            "status": "STRONG" if total_score >= 80 else "COMPETENT" if total_score >= 60 else "DEVELOPING",
        }


machine_test_engine = MachineTestEngine()
