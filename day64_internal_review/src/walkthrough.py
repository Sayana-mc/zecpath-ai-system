"""Run a synthetic candidate through the repository's implemented stages."""

from __future__ import annotations

import json
import re
import sys
import time
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
DAY64 = ROOT / "day64_internal_review"
DATASET = ROOT / "day63_demo_dataset_creation" / "output" / "demo_dataset.json"
CASE_FILE = DAY64 / "data" / "demo_case.json"
OUTPUT_JSON = DAY64 / "output" / "end_to_end_walkthrough.json"
OUTPUT_MARKDOWN = DAY64 / "output" / "end_to_end_walkthrough.md"

DAY26_SRC = ROOT / "day26_screening_scoring_engine" / "src"
if str(DAY26_SRC) not in sys.path:
    sys.path.insert(0, str(DAY26_SRC))

from day10_experience_relevance.src.relevance_scorer import (  # noqa: E402
    calculate_relevance_score,
)
from day11_education_certification.src.education_parser import (  # noqa: E402
    parse_education_section,
)
from day11_education_certification.src.education_relevance import (  # noqa: E402
    calculate_education_relevance,
)
from day13_ats_scoring.src.ats_scoring_engine import (  # noqa: E402
    generate_score_breakdown,
)
from day26_screening_scoring_engine.src.scoring_engine import (  # noqa: E402
    ScreeningScoringEngine,
)
from day32_screening_system_finalization.src.screening_pipeline import (  # noqa: E402
    ScreeningPipeline,
)
from day33_hr_interview_engine.src.interview_flow import (  # noqa: E402
    InterviewFlow,
)
from day37_hr_interview_scoring_engine.config.scoring_config import (  # noqa: E402
    load_config as load_hr_config,
)
from day37_hr_interview_scoring_engine.src.hr_scoring_engine import (  # noqa: E402
    HRInterviewScoringEngine,
)
from day47_technical_skill_scoring.src.scoring_engine import (  # noqa: E402
    build_evaluation_report,
)
from day50_machine_test_ai_design.src.evaluator import (  # noqa: E402
    evaluate_submission,
    load_json,
)
from day51_cross_round_aggregation_engine.src.aggregation_engine import (  # noqa: E402
    aggregate_candidate,
)
from day52_final_recommendation_ai.src.decision_engine import (  # noqa: E402
    recommend_candidate,
)


def _read_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def _timed(
    timings: dict[str, float],
    stage: str,
    operation: Callable[[], Any],
) -> Any:
    started = time.perf_counter()
    try:
        return operation()
    finally:
        timings[stage] = round((time.perf_counter() - started) * 1000, 3)


def _tokens(text: str) -> set[str]:
    return set(re.findall(r"[a-z0-9]+", text.casefold()))


def _lexical_similarity(resume_text: str, job_text: str) -> float:
    resume_tokens = _tokens(resume_text)
    job_tokens = _tokens(job_text)
    if not resume_tokens or not job_tokens:
        return 0.0
    return round(
        100 * len(resume_tokens & job_tokens) / len(resume_tokens | job_tokens),
        2,
    )


def _run_ats(candidate: dict[str, Any]) -> dict[str, Any]:
    resume_text = candidate["resume_text"]
    job = candidate["job_description"]
    required_skills = job["required_skills"]
    matched_skills = [
        skill
        for skill in required_skills
        if skill.casefold() in resume_text.casefold()
    ]
    skill_match = (
        100 * len(matched_skills) / len(required_skills)
        if required_skills
        else 0.0
    )

    experience_line = next(
        (
            line.partition(":")[2].strip()
            for line in resume_text.splitlines()
            if line.casefold().startswith("experience:")
        ),
        "",
    )
    experience_title = experience_line.split(",", maxsplit=1)[0].strip()
    experience = calculate_relevance_score(
        [{"job_title": experience_title}],
        "data analyst",
    )

    education_text = "\n".join(
        line.partition(":")[2].strip()
        for line in resume_text.splitlines()
        if line.casefold().startswith("education:")
    )
    education_records = parse_education_section(education_text)
    education = calculate_education_relevance(
        education_records,
        "data analyst",
    )

    lexical_similarity = _lexical_similarity(
        resume_text,
        " ".join(
            [
                job["title"],
                *job["required_skills"],
                *job.get("preferred_skills", []),
                *job.get("responsibilities", []),
            ]
        ),
    )
    components = {
        "skill_match": round(skill_match, 2),
        "experience_relevance": experience["relevance_score"],
        "education_alignment": round(education["score"] * 100, 2),
        "semantic_similarity": lexical_similarity,
    }
    scored = generate_score_breakdown(
        **components,
        role="data analyst",
    )
    return {
        "score": scored["final_score"],
        "classification": scored["classification"],
        "components": components,
        "matched_required_skills": matched_skills,
        "missing_required_skills": [
            skill for skill in required_skills if skill not in matched_skills
        ],
        "experience_evidence": experience,
        "education_evidence": education,
        "similarity_mode": "lexical_overlap_proxy_not_semantic_embedding",
        "scoring_weights": scored["weights"],
    }


def _run_screening(candidate_id: str, case: dict[str, Any]) -> dict[str, Any]:
    answers = case["screening_answers"]
    answer_map = {answer["question_id"]: answer["answer"] for answer in answers}
    pipeline_result = ScreeningPipeline().process_candidate(
        candidate_id,
        answer_map,
    )
    required_answers = [
        answer
        for answer in pipeline_result["answers"]
        if answer["status"] != "processed"
    ]
    if required_answers:
        missing_ids = ", ".join(item["question_id"] for item in required_answers)
        raise ValueError(f"Screening is incomplete; missing answers: {missing_ids}")

    scoring_config = _read_json(
        ROOT
        / "day26_screening_scoring_engine"
        / "config"
        / "scoring_parameters.json"
    )
    scoring_engine = ScreeningScoringEngine(scoring_config)
    scored_answers = []
    for answer in answers:
        item = dict(answer)
        item["candidate_id"] = candidate_id
        scored_answers.append(item)
    score = scoring_engine.score_candidate(scored_answers)
    return {
        "status": pipeline_result["status"],
        "screening_id": pipeline_result["screening_id"],
        "questions_processed": len(pipeline_result["answers"]),
        "score": score["total_screening_score"],
        "question_scores": score["question_scores"],
        "scoring_mode": "rule_based_demo_heuristics",
    }


def _run_hr_interview(
    candidate_id: str,
    case: dict[str, Any],
) -> dict[str, Any]:
    flow = InterviewFlow()
    phases = [flow.current_phase()]
    while not flow.is_completed():
        phases.append(flow.move_next())
    ratings = case["hr_parameter_scores"]
    score = HRInterviewScoringEngine(load_hr_config()).calculate_candidate_score(
        responses=len(phases),
        relevance=ratings["answer_relevance"],
        communication=ratings["communication"],
        confidence=ratings["confidence"],
        consistency=ratings["consistency"],
    )
    return {
        "candidate_id": candidate_id,
        "completed_phases": phases,
        "score": score["normalized_score"],
        "rubric_input": ratings,
        "score_provenance": "synthetic_demo_ratings_not_reviewer_feedback",
        "explainable_breakdown": score["explainable_breakdown"],
    }


def _run_technical_interview(
    candidate_id: str,
    case: dict[str, Any],
) -> dict[str, Any]:
    answers = []
    for source in case["technical_answers"]:
        answer = dict(source)
        answer.update(
            {
                "candidate_id": candidate_id,
                "candidate_name": "Synthetic Day 64 Candidate",
                "role": "Data Analyst",
            }
        )
        answers.append(answer)
    rubric = _read_json(
        ROOT
        / "day47_technical_skill_scoring"
        / "config"
        / "scoring_rubric.json"
    )
    report = build_evaluation_report(answers, rubric)
    return {
        "score": report["overall_score"],
        "question_count": report["question_count"],
        "skill_wise_breakdown": report["skill_wise_breakdown"],
        "evaluation_mode": report["evaluation_mode"],
        "score_provenance": "synthetic_manual_rubric_inputs",
    }


def _run_machine_test(
    candidate_id: str,
    session_id: str,
    case: dict[str, Any],
) -> dict[str, Any]:
    data = {
        "session_id": session_id,
        "candidate_id": candidate_id,
        **case["machine_test"],
    }
    config = load_json(
        ROOT / "day50_machine_test_ai_design" / "config" / "scoring_rules.json"
    )
    result = evaluate_submission(data, config)
    return {
        "score": result["final_score"],
        "test_results": result["test_results"],
        "review_flags": result["review_flags"],
        "evaluation_limitations": result["limitations"],
        "score_provenance": "supplied_synthetic_execution_and_rubric_results",
    }


def run_walkthrough(
    dataset_path: Path = DATASET,
    case_path: Path = CASE_FILE,
    output_json: Path | None = OUTPUT_JSON,
) -> dict[str, Any]:
    """Run a complete, local, synthetic ATS-to-recommendation walkthrough."""
    started = time.perf_counter()
    timings: dict[str, float] = {}
    candidates = _read_json(dataset_path)["candidates"]
    case = _read_json(case_path)
    candidate = next(
        (
            item
            for item in candidates
            if item["candidate_id"] == case["candidate_id"]
        ),
        None,
    )
    if candidate is None:
        raise ValueError(
            f"Demo candidate {case['candidate_id']} is missing from {dataset_path}"
        )
    if candidate["job_description"] is None:
        raise ValueError("The walkthrough requires a linked job description.")
    if not case.get("synthetic_demo_only"):
        raise ValueError("The walkthrough accepts synthetic demo data only.")

    candidate_id = case["candidate_id"]
    session_id = case["session_id"]
    stage_order = [
        "ats",
        "screening",
        "hr_interview",
        "technical_interview",
        "machine_test",
        "aggregation",
        "decision",
    ]
    stages = {
        "ats": _timed(timings, "ats", lambda: _run_ats(candidate)),
        "screening": _timed(
            timings,
            "screening",
            lambda: _run_screening(candidate_id, case),
        ),
        "hr_interview": _timed(
            timings,
            "hr_interview",
            lambda: _run_hr_interview(candidate_id, case),
        ),
        "technical_interview": _timed(
            timings,
            "technical_interview",
            lambda: _run_technical_interview(candidate_id, case),
        ),
        "machine_test": _timed(
            timings,
            "machine_test",
            lambda: _run_machine_test(candidate_id, session_id, case),
        ),
    }

    scores = {
        "ats": stages["ats"]["score"],
        "screening": stages["screening"]["score"],
        "hr_interview": stages["hr_interview"]["score"],
        "technical_interview": stages["technical_interview"]["score"],
        "machine_test": stages["machine_test"]["score"],
    }
    aggregation_input = {
        "candidate_id": candidate_id,
        "session_id": session_id,
        "role": case["role"],
        "evaluations": {
            name: {
                "status": "completed",
                "score": score,
                "maximum_score": 100,
            }
            for name, score in scores.items()
        },
    }
    aggregation_config = _read_json(
        ROOT
        / "day51_cross_round_aggregation_engine"
        / "config"
        / "role_weights.json"
    )
    stages["aggregation"] = _timed(
        timings,
        "aggregation",
        lambda: aggregate_candidate(aggregation_input, aggregation_config),
    )
    aggregation = stages["aggregation"]
    if aggregation["score_status"] != "COMPLETE":
        raise ValueError(
            "Decision cannot proceed: not all required evaluation rounds completed."
        )

    decision_assessment = {
        "candidate_id": candidate_id,
        "session_id": session_id,
        "target_role": case["role"],
        "assessment_status": aggregation["score_status"],
        "unified_score": aggregation["hiring_fit_score_percent"],
        "completed_rounds": len(scores),
        "expected_rounds": len(scores),
        "evidence_quality": case["evidence_quality"],
        "data_consistency": case["data_consistency"],
        "risk_factors": {
            "integrity": {
                "flag": False,
                "evidence": [],
                "source": "No finding asserted in synthetic walkthrough",
            },
            "behavior": {
                "flag": False,
                "evidence": [],
                "source": "No finding asserted in synthetic walkthrough",
            },
        },
        "rounds": scores,
    }
    decision_rules = _read_json(
        ROOT
        / "day52_final_recommendation_ai"
        / "config"
        / "decision_rules.json"
    )
    stages["decision"] = _timed(
        timings,
        "decision",
        lambda: recommend_candidate(decision_assessment, decision_rules),
    )

    limitations = [
        "All inputs in this walkthrough are synthetic demonstration data.",
        "ATS semantic_similarity is a lexical-overlap proxy, not an embedding model.",
        "Screening scores use heuristic rules and are not validated measures.",
        "HR parameter scores and technical rubric scores are supplied demo ratings, not reviewer feedback.",
        "Machine-test execution results and rubric metrics are supplied; submitted code is not executed by the prototype.",
        "No external ATS, voice, database, authentication, or deployed service is integrated.",
        "The recommendation is advisory only; no human disposition or employment action is made.",
    ]
    report = {
        "report_name": "Day 64 Synthetic End-to-End Walkthrough",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "test_mode": "SYNTHETIC_LOCAL_INTEGRATION",
        "candidate_id": candidate_id,
        "session_id": session_id,
        "stage_order": stage_order,
        "stages": stages,
        "human_review": {
            "required": True,
            "disposition": "PENDING",
            "automatic_employment_action": False,
        },
        "performance": {
            "stage_latency_ms": timings,
            "total_pipeline_ms": round(
                (time.perf_counter() - started) * 1000,
                3,
            ),
            "scope": (
                "Single local synthetic run; not a load test and excludes "
                "network, storage, external models, and production services."
            ),
        },
        "limitations": limitations,
    }
    if output_json is not None:
        output_json = Path(output_json)
        output_json.parent.mkdir(parents=True, exist_ok=True)
        output_json.write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        markdown_path = output_json.with_suffix(".md")
        markdown_path.write_text(_to_markdown(report), encoding="utf-8")
    return report


def _to_markdown(report: dict[str, Any]) -> str:
    stages = report["stages"]
    lines = [
        "# Day 64 - Synthetic End-to-End Walkthrough",
        "",
        f"- Candidate: `{report['candidate_id']}` (synthetic demo)",
        f"- Session: `{report['session_id']}`",
        f"- Generated: {report['generated_at']}",
        f"- Mode: `{report['test_mode']}`",
        "",
        "## Stage results",
        "",
        "| Stage | Score / status | Latency (ms) |",
        "|---|---:|---:|",
        f"| ATS | {stages['ats']['score']} | {report['performance']['stage_latency_ms']['ats']} |",
        f"| Screening | {stages['screening']['score']} | {report['performance']['stage_latency_ms']['screening']} |",
        f"| HR interview | {stages['hr_interview']['score']} | {report['performance']['stage_latency_ms']['hr_interview']} |",
        f"| Technical interview | {stages['technical_interview']['score']} | {report['performance']['stage_latency_ms']['technical_interview']} |",
        f"| Machine test | {stages['machine_test']['score']} | {report['performance']['stage_latency_ms']['machine_test']} |",
        f"| Aggregation | {stages['aggregation']['hiring_fit_score_percent']} ({stages['aggregation']['score_status']}) | {report['performance']['stage_latency_ms']['aggregation']} |",
        f"| Decision | {stages['decision']['decision']} (advisory) | {report['performance']['stage_latency_ms']['decision']} |",
        "",
        "## Review safeguards",
        "",
        f"- Human review required: **{report['human_review']['required']}**",
        f"- Human disposition: **{report['human_review']['disposition']}**",
        f"- Automatic employment action: **{report['human_review']['automatic_employment_action']}**",
        "",
        "## Limitations",
        "",
    ]
    lines.extend(f"- {item}" for item in report["limitations"])
    lines.extend(
        [
            "",
            "## Performance scope",
            "",
            f"- Total local runtime: {report['performance']['total_pipeline_ms']} ms",
            f"- {report['performance']['scope']}",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    report = run_walkthrough()
    print(f"Day 64 synthetic walkthrough: {report['candidate_id']}")
    print(f"Stages: {' -> '.join(report['stage_order'])}")
    print(
        "Advisory: "
        f"{report['stages']['decision']['decision']} "
        "(human disposition pending)"
    )
    print(f"Output: {OUTPUT_JSON}")
    print(f"Total local runtime: {report['performance']['total_pipeline_ms']} ms")


if __name__ == "__main__":
    main()
