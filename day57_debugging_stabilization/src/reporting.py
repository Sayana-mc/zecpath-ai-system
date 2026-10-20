"""Versioned and deterministic JSON/Markdown reporting."""
from datetime import datetime, timezone
import json

def create_report(config, results, performance):
    return {"report_schema_version": "1.0", "project_name": config["project_name"], "module_version": config["version"],
        "generated_at_utc": datetime.now(timezone.utc).isoformat(), "test_mode": "SYNTHETIC_LOCAL_STABILIZATION",
        "candidate_results": results, "performance_analysis": performance,
        "recommendations": [
            "Keep human review mandatory and automatic rejection disabled.",
            "Investigate score gaps and ATS-versus-interview contradictions before changing weights.",
            "Add broader edge-case and integration tests before connecting live services.",
            "Benchmark production latency only after model, database, storage and network integrations exist.",
            "Use authorized representative data and documented human evaluation before assessing hiring validity.",
            "The Day 56 simulation has no conversation-state module; validate the actual conversation component separately if it exists in the wider system."
        ],
        "limitations": ["All records are synthetic.", "ATS scoring is keyword coverage, not a trained model.",
            "Human judgments are supplied test labels, not independently verified ground truth.",
            "No external API, database, or production infrastructure is exercised.",
            "Conversation logic is outside this module because no conversation engine is included in the Day 56 simulation package."]}

def to_markdown(report):
    p = report["performance_analysis"]
    lines = ["# Day 57 — Debugging & Stabilization Report", "", f"- Project: {report['project_name']}",
        f"- Module version: {report['module_version']}", f"- Generated (UTC): {report['generated_at_utc']}",
        f"- Test mode: {report['test_mode']}", "", "## Executive summary", f"- Candidates: {p['candidate_count']}",
        f"- Successful candidates: {p['successful_candidates']}", f"- Failed candidates: {p['failed_candidates']}",
        f"- Stage completion rate: {p['stage_completion_rate_percent']}%", f"- Inconsistencies: {p['inconsistency_count']}",
        f"- Average pipeline time for successful candidates: {p['average_pipeline_ms_successful_candidates']} ms", "",
        "## Candidate status", "", "| Candidate ID | Candidate | Status | Final score | Inconsistencies | Error |", "|---|---|---|---:|---:|---|"]
    for r in report["candidate_results"]:
        final = r.get("stages", {}).get("final_decision", {})
        lines.append(f"| {r.get('candidate_id','UNKNOWN')} | {r.get('candidate_name','UNKNOWN')} | {r.get('status','UNKNOWN')} | {final.get('final_score','N/A')} | {len(r.get('inconsistencies',[]))} | {r.get('error',{}).get('message','')} |")
    lines += ["", "## Inconsistencies"]
    lines += [f"- **{i['candidate_id']} / {i['type']} ({i['severity']})**: {i['details']}" for i in p["inconsistencies"]] or ["- No configured inconsistencies detected."]
    lines += ["", "## Refined safeguards", "- Human review is mandatory.", "- Automatic rejection is disabled.",
        "- Input JSON, configuration, scores, candidate IDs, resume filenames, and decision labels are validated.",
        "- Candidate-level failures are recorded so one bad record does not necessarily stop the batch.",
        "- Output includes a schema version and UTC generation timestamp.", "", "## Recommendations"]
    lines += [f"{i}. {x}" for i, x in enumerate(report["recommendations"], 1)]
    lines += ["", "## Limitations"] + [f"- {x}" for x in report["limitations"]]
    return "\n".join(lines) + "\n"

def validate_report_shape(report):
    required = {"report_schema_version", "project_name", "module_version", "generated_at_utc", "test_mode", "candidate_results", "performance_analysis", "recommendations", "limitations"}
    missing = required - set(report)
    if missing:
        raise ValueError(f"Report missing required keys: {', '.join(sorted(missing))}")
    if not isinstance(report["candidate_results"], list) or not isinstance(report["performance_analysis"], dict):
        raise ValueError("Report candidate_results/performance_analysis has an invalid type.")
    return report

def write_json_atomic(path, payload):
    """Write a complete JSON file via temp file then replace target."""
    from pathlib import Path
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(payload, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
    temp.replace(path)
