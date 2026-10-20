import json
from pathlib import Path
from .pipeline import load_json, run_candidate, summarize
from .reporting import create_report, to_markdown

ROOT=Path(__file__).resolve().parents[1]

def main():
    config=load_json(ROOT/"config"/"pipeline_config.json")
    candidates=load_json(ROOT/"data"/"candidates.json")
    results=[run_candidate(c,config,ROOT/"data") for c in candidates]
    performance=summarize(results)
    report=create_report(config,results,performance)
    out=ROOT/"output"; out.mkdir(exist_ok=True)
    (out/"end_to_end_test_report.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    (out/"end_to_end_test_report.md").write_text(to_markdown(report),encoding="utf-8")
    (out/"performance_analysis.json").write_text(json.dumps(performance,indent=2),encoding="utf-8")
    (out/"improvement_recommendations.md").write_text("# Day 56 — Improvement Recommendations\n\n"+"\n".join(f"{i}. {x}" for i,x in enumerate(report["recommendations"],1))+"\n",encoding="utf-8")
    print("DAY 56 — FULL SYSTEM SIMULATION")
    print(f"Candidates simulated: {performance['candidate_count']}")
    print(f"Stage completion rate: {performance['stage_completion_rate_percent']}%")
    print(f"Average pipeline time: {performance['average_pipeline_ms']} ms")
    print(f"AI/human match rate: {performance['judgment_match_rate_percent']}%")
    print(f"Inconsistencies detected: {performance['inconsistency_count']}")
    print(f"Reports generated: {out}")

if __name__=="__main__":
    main()
