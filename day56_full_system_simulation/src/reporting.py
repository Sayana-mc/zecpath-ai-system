from datetime import datetime, timezone

def create_report(config, results, performance):
    recommendations = [
        "Investigate candidates with score gaps above the configured threshold before changing scoring weights.",
        "Review ATS/interview contradictions; keyword coverage alone should not determine suitability.",
        "Validate thresholds and weights using a larger representative dataset reviewed by qualified humans.",
        "Record missing stages explicitly; do not treat missing scores as zero.",
        "Measure production latency with real database, file storage, network and model inference integrations.",
        "Keep consent, audit logging, access controls and human review safeguards from Day 55."
    ]
    return {"project_name":config["project_name"],"version":config["version"],
        "generated_at":datetime.now(timezone.utc).isoformat(),
        "test_mode":"SYNTHETIC_LOCAL_SIMULATION","candidate_results":results,
        "performance_analysis":performance,"recommendations":recommendations}

def to_markdown(report):
    p=report["performance_analysis"]
    lines=["# Day 56 — End-to-End AI Test Report","",
        f"- Project: {report['project_name']}",f"- Version: {report['version']}",
        f"- Generated: {report['generated_at']}",f"- Test mode: {report['test_mode']}","",
        "## Executive summary",f"- Candidates simulated: {p['candidate_count']}",
        f"- Stage completion rate: {p['stage_completion_rate_percent']}%",
        f"- Average pipeline time: {p['average_pipeline_ms']} ms",
        f"- AI/human judgment match rate: {p['judgment_match_rate_percent']}%",
        f"- Inconsistencies detected: {p['inconsistency_count']}","",
        "## Candidate comparison","",
        "| Candidate | AI score | AI advisory | Human judgment | Score gap | Match | Issues |",
        "|---|---:|---|---|---:|---|---:|"]
    for r in report["candidate_results"]:
        f=r["stages"]["final_decision"]; h=r["human_comparison"]
        lines.append(f"| {r['candidate_id']} | {f['final_score']} | {f['ai_advisory']} | {h['human_judgment']} | {h['score_gap']} | {'Yes' if h['judgment_matches'] else 'No'} | {len(r['inconsistencies'])} |")
    lines += ["","## Inconsistencies"]
    lines += ([f"- **{i['candidate_id']} / {i['type']} ({i['severity']})**: {i['details']}" for i in p["inconsistencies"]]
              or ["No configured inconsistencies detected."])
    lines += ["","## Performance analysis",f"- Total stage executions: {p['total_stage_executions']}",
        f"- Completed stage executions: {p['completed_stage_executions']}",
        f"- Failed stage executions: {p['failed_stage_executions']}",
        f"- Average latency per stage (ms): `{p['average_stage_latency_ms']}`",
        f"- Scope: {p['performance_scope']}","","## Improvement recommendations"]
    lines += [f"{i}. {x}" for i,x in enumerate(report["recommendations"],1)]
    lines += ["","## Limitations",
        "- All candidates and interview scores are synthetic test inputs.",
        "- ATS scoring is keyword coverage, not a trained model.",
        "- Human labels are supplied simulation labels, not independently verified ground truth.",
        "- Human review is mandatory; automatic rejection is disabled."]
    return "\n".join(lines)+"\n"
