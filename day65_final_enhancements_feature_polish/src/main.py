"""Day 65 local hiring-pipeline quality demonstration."""
import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
CONFIG = ROOT / "config" / "scoring_config.json"
OUTPUT = ROOT / "output"


class DataValidationError(ValueError):
    """Raised when source data is missing or malformed."""


def load_json(path):
    try:
        with path.open("r", encoding="utf-8") as stream:
            return json.load(stream)
    except FileNotFoundError as exc:
        raise DataValidationError(f"Required file not found: {path.name}") from exc
    except json.JSONDecodeError as exc:
        raise DataValidationError(f"Invalid JSON in {path.name}: {exc.msg}") from exc


def validate_inputs(jobs, candidates, config):
    if not isinstance(jobs, list) or not jobs:
        raise DataValidationError("jobs must be a non-empty list")
    if not isinstance(candidates, list) or not candidates:
        raise DataValidationError("candidates must be a non-empty list")
    if not isinstance(config, dict):
        raise DataValidationError("scoring config must be a JSON object")
    job_ids = set()
    for job in jobs:
        for key in ("job_id", "title", "required_skills", "preferred_skills"):
            if key not in job:
                raise DataValidationError(f"Job record missing field: {key}")
        if job["job_id"] in job_ids:
            raise DataValidationError(f"Duplicate job_id: {job['job_id']}")
        job_ids.add(job["job_id"])
        if not job["required_skills"]:
            raise DataValidationError(f"{job['job_id']} must define required skills")
    candidate_ids = set()
    for candidate in candidates:
        for key in ("candidate_id", "name", "job_id", "resume_text",
                    "application_complete", "interview_response_present"):
            if key not in candidate:
                raise DataValidationError(f"Candidate record missing field: {key}")
        if candidate["candidate_id"] in candidate_ids:
            raise DataValidationError(f"Duplicate candidate_id: {candidate['candidate_id']}")
        candidate_ids.add(candidate["candidate_id"])
        if candidate["job_id"] not in job_ids:
            raise DataValidationError(
                f"{candidate['candidate_id']} references unknown job_id {candidate['job_id']}"
            )
    required_weight = config.get("required_skill_weight")
    preferred_weight = config.get("preferred_skill_weight")
    if not isinstance(required_weight, (int, float)) or not isinstance(preferred_weight, (int, float)):
        raise DataValidationError("Scoring weights must be numeric")
    if abs(required_weight + preferred_weight - 1.0) > 1e-9:
        raise DataValidationError("Scoring weights must sum to 1.0")
    if config.get("automated_rejection_enabled") is not False:
        raise DataValidationError("Demo safety setting must keep automated rejection disabled")


def find_skills(text, skills):
    found = []
    for skill in skills:
        pattern = r"(?<![a-z0-9])" + re.escape(skill.lower()) + r"(?![a-z0-9])"
        if re.search(pattern, text.lower()):
            found.append(skill)
    return found


def score_candidate(candidate, job, config):
    required = job["required_skills"]
    preferred = job["preferred_skills"]
    required_found = find_skills(candidate["resume_text"], required)
    preferred_found = find_skills(candidate["resume_text"], preferred)
    required_pct = 100 * len(required_found) / len(required)
    preferred_pct = 100 * len(preferred_found) / len(preferred) if preferred else 0
    score = (
        config["required_skill_weight"] * required_pct
        + config["preferred_skill_weight"] * preferred_pct
    )
    score = round(max(config["score_min"], min(config["score_max"], score)),
                  config["display_precision"])

    flags = []
    if not candidate["application_complete"]:
        flags.append("Application information incomplete")
    if len(required_found) < len(required):
        flags.append("Some required skills are not evidenced in resume")
    lowered = candidate["resume_text"].lower()
    if "details not available" in lowered or "conflicts" in lowered:
        flags.append("Resume details need clarification")

    if flags:
        status = "HUMAN_REVIEW_REQUIRED"
    elif candidate["interview_response_present"]:
        status = "INTERVIEW_REVIEW"
    else:
        status = "SCREENING_REVIEW"

    return {
        "candidate_id": candidate["candidate_id"],
        "candidate_name": candidate["name"],
        "job_id": job["job_id"],
        "job_title": job["title"],
        "score_percent": score,
        "required_skills_found": required_found,
        "required_skills_total": len(required),
        "preferred_skills_found": preferred_found,
        "preferred_skills_total": len(preferred),
        "application_complete": candidate["application_complete"],
        "interview_response_present": candidate["interview_response_present"],
        "review_flags": flags,
        "status": status,
        "human_review_required": True,
        "automated_rejection": False,
        "scoring_version": config["version"],
    }


def run():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    jobs = load_json(DATA / "jobs.json")
    candidates = load_json(DATA / "candidates.json")
    config = load_json(CONFIG)
    validate_inputs(jobs, candidates, config)
    job_lookup = {job["job_id"]: job for job in jobs}
    results = [score_candidate(c, job_lookup[c["job_id"]], config) for c in candidates]

    summary = {
        "report_title": "Day 65 Recruiter Review Summary",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "scoring_version": config["version"],
        "simulation_only": True,
        "candidate_count": len(results),
        "job_count": len(jobs),
        "human_review_required_count": sum(r["human_review_required"] for r in results),
        "automated_rejection_enabled": False,
        "records": results,
    }
    (OUTPUT / "recruiter_summary.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )

    columns = [
        "candidate_id", "candidate_name", "job_id", "job_title", "score_percent",
        "status", "application_complete", "interview_response_present",
        "review_flags", "human_review_required", "automated_rejection",
        "scoring_version"
    ]
    with (OUTPUT / "recruiter_summary.csv").open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        for record in results:
            row = dict(record)
            row["review_flags"] = "; ".join(record["review_flags"])
            writer.writerow({key: row.get(key) for key in columns})

    status_counts = {}
    for record in results:
        status_counts[record["status"]] = status_counts.get(record["status"], 0) + 1
    report = [
        "Day 65 final enhancements demo completed.",
        f"Candidates processed: {len(results)}",
        f"Job descriptions: {len(jobs)}",
        f"Human review required: {summary['human_review_required_count']}",
        f"Scoring version: {config['version']}",
        "Automated rejection: disabled",
        "External ATS/API: not called",
        "Simulation only: yes",
        "Status counts: " + json.dumps(status_counts, sort_keys=True),
        f"JSON report: {OUTPUT / 'recruiter_summary.json'}",
        f"CSV report: {OUTPUT / 'recruiter_summary.csv'}",
    ]
    (OUTPUT / "run_report.txt").write_text("\n".join(report) + "\n", encoding="utf-8")
    print("\n".join(report))
    return results


if __name__ == "__main__":
    try:
        run()
    except DataValidationError as error:
        print(f"DATA VALIDATION ERROR: {error}")
        raise SystemExit(2)
    except OSError as error:
        print(f"FILE SYSTEM ERROR: {error}")
        raise SystemExit(3)
