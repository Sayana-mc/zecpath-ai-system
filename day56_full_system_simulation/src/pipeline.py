import json, time
from pathlib import Path
from statistics import mean

def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def run_candidate(candidate, config, data_dir):
    timings, statuses = {}, {}
    def run_stage(name, fn):
        start = time.perf_counter()
        try:
            result = fn()
            statuses[name] = "COMPLETED"
            return result
        except Exception as exc:
            statuses[name] = "FAILED"
            raise RuntimeError(f"{name} failed: {exc}") from exc
        finally:
            timings[name] = round((time.perf_counter() - start) * 1000, 3)

    resume_path = Path(data_dir) / "resumes" / candidate["resume_file"]
    resume = run_stage("resume_upload", lambda: read_resume(resume_path))
    required = config["required_skills"]
    text = resume["text"].lower()
    matched = [skill for skill in required if skill.lower() in text]
    ats = run_stage("ats_scoring", lambda: {
        "score": round(100 * len(matched) / max(len(required), 1), 2),
        "matched_skills": matched,
        "missing_skills": [skill for skill in required if skill not in matched]
    })
    screening = run_stage("screening", lambda: valid_score(candidate["screening_score"]))
    hr = run_stage("hr_interview", lambda: valid_score(candidate["hr_interview_score"]))
    technical = run_stage("technical_interview", lambda: valid_score(candidate["technical_interview_score"]))
    machine = run_stage("machine_test", lambda: valid_score(candidate["machine_test_score"]))

    def final_stage():
        weights = config["stage_weights"]
        scores = {"ats": ats["score"], "screening": screening, "hr_interview": hr,
                  "technical_interview": technical, "machine_test": machine}
        if set(weights) != set(scores) or abs(sum(weights.values()) - 1.0) > 1e-6:
            raise ValueError("Stage weights must match scores and sum to 1.0.")
        score = round(sum(scores[k] * weights[k] for k in weights), 2)
        if score >= config["thresholds"]["strong_fit"]:
            advisory = "SELECTED_FOR_HUMAN_REVIEW"
            comparison_label = "SELECTED"
        elif score >= config["thresholds"]["potential_fit"]:
            advisory = "HOLD_REVIEW"
            comparison_label = "HOLD_REVIEW"
        else:
            advisory = "FURTHER_REVIEW_REQUIRED"
            comparison_label = "REJECTED"  # comparison mapping only; no automatic rejection
        return {"round_scores": scores, "final_score": score, "ai_advisory": advisory,
                "comparison_label_only": comparison_label,
                "human_review_required": config["governance"]["human_review_required"],
                "automatic_rejection_enabled": config["governance"]["automatic_rejection_enabled"]}
    final = run_stage("final_decision", final_stage)

    human_label = candidate["human_judgment"]
    gap = round(abs(final["final_score"] - valid_score(candidate["human_score"])), 2)
    issues = []
    if gap > config["inconsistency"]["score_gap_threshold"]:
        issues.append({"type":"SCORE_GAP","severity":"HIGH","details":f"AI and human scores differ by {gap} points."})
    if final["comparison_label_only"] != human_label:
        issues.append({"type":"JUDGMENT_MISMATCH","severity":"REVIEW","details":f"AI comparison label is {final['comparison_label_only']}; human label is {human_label}."})
    if ats["score"] >= 80 and min(hr, technical, machine) < 60:
        issues.append({"type":"ATS_INTERVIEW_CONTRADICTION","severity":"REVIEW","details":"Strong ATS keyword coverage conflicts with a low interview/test score."})

    stages = {
        "resume_upload":{"status":statuses["resume_upload"],"file_name":resume["file_name"],"character_count":resume["character_count"]},
        "ats_scoring":{"status":statuses["ats_scoring"],**ats},
        "screening":{"status":statuses["screening"],"score":screening},
        "hr_interview":{"status":statuses["hr_interview"],"score":hr},
        "technical_interview":{"status":statuses["technical_interview"],"score":technical},
        "machine_test":{"status":statuses["machine_test"],"score":machine},
        "final_decision":{"status":statuses["final_decision"],**final}
    }
    return {"candidate_id":candidate["candidate_id"],"candidate_name":candidate["name"],
            "stages":stages,
            "human_comparison":{"human_judgment":human_label,"human_score":candidate["human_score"],
                "score_gap":gap,"judgment_matches":final["comparison_label_only"] == human_label,
                "human_notes":candidate.get("human_notes","")},
            "inconsistencies":issues,"performance_ms":timings,
            "total_pipeline_ms":round(sum(timings.values()),3)}

def read_resume(path):
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Resume file missing: {path.name}")
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        raise ValueError("Resume is empty.")
    return {"file_name":path.name,"character_count":len(text),"text":text}

def valid_score(value):
    if isinstance(value, bool) or not isinstance(value, (int,float)) or not 0 <= value <= 100:
        raise ValueError(f"Score must be a number from 0 to 100: {value}")
    return float(value)

def summarize(results):
    stages = ["resume_upload","ats_scoring","screening","hr_interview","technical_interview","machine_test","final_decision"]
    count = len(results)
    total = count * len(stages)
    done = sum(1 for r in results for s in r["stages"].values() if s["status"] == "COMPLETED")
    matches = sum(1 for r in results if r["human_comparison"]["judgment_matches"])
    issues = [{"candidate_id":r["candidate_id"],**i} for r in results for i in r["inconsistencies"]]
    return {
        "candidate_count":count,"stage_count_per_candidate":len(stages),"total_stage_executions":total,
        "completed_stage_executions":done,"failed_stage_executions":total-done,
        "stage_completion_rate_percent":round(done/total*100,2) if total else 0,
        "average_pipeline_ms":round(mean(r["total_pipeline_ms"] for r in results),3) if results else 0,
        "average_stage_latency_ms":{s:round(mean(r["performance_ms"][s] for r in results),3) for s in stages} if results else {},
        "ai_human_judgment_matches":matches,"ai_human_judgment_mismatches":count-matches,
        "judgment_match_rate_percent":round(matches/count*100,2) if count else 0,
        "inconsistency_count":len(issues),"inconsistencies":issues,
        "performance_scope":"Local synthetic-data simulation; excludes network, database, real model inference, and external ATS integrations."
    }
