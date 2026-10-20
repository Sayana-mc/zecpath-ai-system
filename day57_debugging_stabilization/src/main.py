"""Day 57 command-line entry point."""
from pathlib import Path
import sys
from .validation import load_json, validate_config, validate_candidates, ValidationError
from .pipeline import run_candidate, summarize
from .reporting import create_report, to_markdown, validate_report_shape, write_json_atomic

ROOT = Path(__file__).resolve().parents[1]

def main():
    try:
        config = validate_config(load_json(ROOT / "config" / "stabilization_config.json"))
        candidates = validate_candidates(load_json(ROOT / "data" / "candidates.json"))
    except ValidationError as exc:
        print(f"CONFIGURATION / INPUT ERROR: {exc}", file=sys.stderr)
        return 2
    results = []
    for candidate in candidates:
        result = run_candidate(candidate, config, ROOT / "data")
        results.append(result)
        if result["status"] == "FAILED":
            print(f"WARNING: candidate {result['candidate_id']} failed: {result['error']['message']}", file=sys.stderr)
            if not config["continue_on_candidate_error"]:
                break
    performance = summarize(results)
    report = validate_report_shape(create_report(config, results, performance))
    out = ROOT / "output"
    try:
        write_json_atomic(out / "debugging_report.json", report)
        (out / "debugging_report.md").write_text(to_markdown(report), encoding="utf-8")
        write_json_atomic(out / "system_stability_summary.json", performance)
        recommendation_text = "# Day 57 — Improvement Recommendations\n\n" + "\n".join(f"{i}. {x}" for i, x in enumerate(report["recommendations"], 1)) + "\n"
        (out / "improvement_recommendations.md").write_text(recommendation_text, encoding="utf-8")
    except OSError as exc:
        print(f"OUTPUT ERROR: could not write reports: {exc}", file=sys.stderr)
        return 3
    print("DAY 57 — DEBUGGING & STABILIZATION")
    print(f"Candidates processed: {performance['candidate_count']}")
    print(f"Successful candidates: {performance['successful_candidates']}")
    print(f"Failed candidates: {performance['failed_candidates']}")
    print(f"Stage completion rate: {performance['stage_completion_rate_percent']}%")
    print(f"Inconsistencies detected: {performance['inconsistency_count']}")
    print(f"Human review required: {performance['human_review_required']}")
    print(f"Automatic rejection enabled: {performance['automatic_rejection_enabled']}")
    print(f"Reports generated: {out}")
    return 0 if performance["failed_candidates"] == 0 else 1

if __name__ == "__main__":
    raise SystemExit(main())
