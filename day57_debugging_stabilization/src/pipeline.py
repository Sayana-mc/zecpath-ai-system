"""Stable deterministic simulation pipeline; no external AI/API calls are made."""
from pathlib import Path
import re
import time
from statistics import mean
from .validation import ValidationError, validate_score

STAGES = ["resume_upload", "ats_scoring", "screening", "hr_interview", "technical_interview", "machine_test", "final_decision"]

def read_resume(path, max_characters=200000):
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"Resume file missing: {path.name}")
    text = path.read_text(encoding="utf-8-sig").strip()
    if not text:
        raise ValueError("Resume is empty.")
    if len(text) > max_characters:
        raise ValueError(f"Resume exceeds configured limit of {max_characters} characters.")
    return {"file_name": path.name, "character_count": len(text), "text": text}

def keyword_matches(text, skills):
    """Case-insensitive whole-token matching, avoiding 'sql' inside 'nosql'."""
    normalized = text.casefold()
    matched, missing = [], []
    for skill in skills:
        pattern = r"(?<![a-z0-9])" + re.escape(skill.casefold()) + r"(?![a-z0-9])"
        (matched if re.search(pattern, normalized) else missing).append(skill)
    return matched, missing

def score_to_advisory(score, thresholds):
    # No label here triggers a hiring action; every outcome requires human review.
    if score >= thresholds["strong_fit"]:
        return "STRONG_FIT_REVIEW_REQUIRED"
    if score >= thresholds["potential_fit"]:
        return "POTENTIAL_FIT_REVIEW_REQUIRED"
    return "ADDITIONAL_REVIEW_REQUIRED"

def run_candidate(candidate, config, data_dir):
    timings, stages, issues = {}, {}, []
    def stage(name, fn):
        started = time.perf_counter()
        try:
            value = fn()
            stages[name] = {"status": "COMPLETED"}
            return value
        except (OSError, ValueError, TypeError, KeyError, ValidationError) as exc:
            stages[name] = {"status": "FAILED", "error_type": type(exc).__name__, "error": str(exc)}
            raise
        finally:
            timings[name] = round((time.perf_counter() - started) * 1000, 3)

    try:
        resume = stage("resume_upload", lambda: read_resume(Path(data_dir) / "resumes" / candidate["resume_file"], config["max_resume_characters"]))
        stages["resume_upload"].update({"file_name": resume["file_name"], "character_count": resume["character_count"]})
        matched, missing = stage("ats_scoring", lambda: keyword_matches(resume["text"], config["required_skills"]))
        ats = {"score": round(100 * len(matched) / len(config["required_skills"]), 2), "matched_skills": matched, "missing_skills": missing}
        stages["ats_scoring"].update(ats)
        scores = {
            "ats": ats["score"],
            "screening": stage("screening", lambda: validate_score(candidate["screening_score"], "screening_score")),
            "hr_interview": stage("hr_interview", lambda: validate_score(candidate["hr_interview_score"], "hr_interview_score")),
            "technical_interview": stage("technical_interview", lambda: validate_score(candidate["technical_interview_score"], "technical_interview_score")),
            "machine_test": stage("machine_test", lambda: validate_score(candidate["machine_test_score"], "machine_test_score")),
        }
        for name in ("screening", "hr_interview", "technical_interview", "machine_test"):
            stages[name]["score"] = scores[name]
        final_score = round(sum(scores[key] * config["stage_weights"][key] for key in config["stage_weights"]), 2)
        advisory = score_to_advisory(final_score, config["thresholds"])
        stages["final_decision"] = {"status": "COMPLETED", "round_scores": scores, "final_score": final_score,
            "ai_advisory": advisory, "human_review_required": True, "automatic_rejection_enabled": False,
            "decision_note": "Advisory only; no automated selection or rejection is performed."}
        timings["final_decision"] = 0.0
        human_score = validate_score(candidate["human_score"], "human_score")
        gap = round(abs(final_score - human_score), 2)
        if gap > config["inconsistency"]["score_gap_threshold"]:
            issues.append({"type": "SCORE_GAP", "severity": "HIGH", "details": f"AI and supplied human scores differ by {gap} points."})
        if scores["ats"] >= 80 and min(scores["hr_interview"], scores["technical_interview"], scores["machine_test"]) < 60:
            issues.append({"type": "ATS_INTERVIEW_CONTRADICTION", "severity": "REVIEW", "details": "Strong ATS keyword coverage conflicts with at least one later-stage score below 60."})
        return {"candidate_id": candidate["candidate_id"], "candidate_name": candidate["name"], "status": "COMPLETED",
            "stages": stages, "human_comparison": {"human_judgment": candidate["human_judgment"], "human_score": human_score,
            "score_gap": gap, "label_match_rate_not_applicable": True,
            "human_notes": candidate.get("human_notes", "")}, "inconsistencies": issues,
            "performance_ms": timings, "total_pipeline_ms": round(sum(timings.values()), 3)}
    except Exception as exc:
        # Candidate-scoped error: caller may continue with other candidates.
        return {"candidate_id": candidate.get("candidate_id", "UNKNOWN"), "candidate_name": candidate.get("name", "UNKNOWN"),
            "status": "FAILED", "stages": stages, "inconsistencies": issues,
            "error": {"type": type(exc).__name__, "message": str(exc)},
            "performance_ms": timings, "total_pipeline_ms": round(sum(timings.values()), 3),
            "human_review_required": True, "automatic_rejection_enabled": False}

def summarize(results):
    count = len(results)
    completed = sum(r.get("status") == "COMPLETED" for r in results)
    all_stage_count = sum(len(r.get("stages", {})) for r in results)
    completed_stages = sum(1 for r in results for s in r.get("stages", {}).values() if s.get("status") == "COMPLETED")
    issues = [{"candidate_id": r.get("candidate_id", "UNKNOWN"), **issue} for r in results for issue in r.get("inconsistencies", [])]
    valid_times = [r.get("total_pipeline_ms", 0) for r in results if r.get("status") == "COMPLETED"]
    return {"candidate_count": count, "successful_candidates": completed, "failed_candidates": count - completed,
        "stage_executions_recorded": all_stage_count, "completed_stage_executions": completed_stages,
        "failed_stage_executions": all_stage_count - completed_stages,
        "stage_completion_rate_percent": round(completed_stages / all_stage_count * 100, 2) if all_stage_count else 0,
        "average_pipeline_ms_successful_candidates": round(mean(valid_times), 3) if valid_times else 0,
        "inconsistency_count": len(issues), "inconsistencies": issues,
        "human_review_required": True, "automatic_rejection_enabled": False,
        "performance_scope": "Local synthetic-data simulation only; excludes external model inference, network, database, and production ATS integrations."}
