"""Build and export the Day 53 Hiring Intelligence Report."""

import json
import math
from pathlib import Path
from typing import Any


ROUND_NAMES = (
    "ats",
    "screening",
    "hr_interview",
    "technical_interview",
    "machine_test",
)
ADVISORY_DISCLAIMER = (
    "This report is advisory only. A qualified human reviewer must verify "
    "the underlying evidence before making any employment decision."
)


class ReportInputError(ValueError):
    """Raised when assessment input cannot produce a reliable report."""


def load_json(path: str | Path) -> Any:
    """Load JSON data from a UTF-8 file."""
    with Path(path).open(encoding="utf-8") as file:
        return json.load(file)


def _require_mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ReportInputError(f"{label} must be a JSON object.")
    return value


def _validate_score(value: Any, label: str) -> float:
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or not math.isfinite(value)
        or not 0 <= value <= 100
    ):
        raise ReportInputError(f"{label} must be a number from 0 to 100.")
    return float(value)


def _string_list(value: Any, label: str) -> list[str]:
    if not isinstance(value, list) or not all(
        isinstance(item, str) for item in value
    ):
        raise ReportInputError(f"{label} must be a list of strings.")
    return value.copy()


def _validate_assessment(assessment: Any) -> dict[str, Any]:
    assessment = _require_mapping(assessment, "Assessment")
    candidate = _require_mapping(assessment.get("candidate"), "candidate")
    for field in ("candidate_id", "name", "target_role"):
        if not isinstance(candidate.get(field), str) or not candidate[field].strip():
            raise ReportInputError(f"candidate.{field} is required.")

    rounds = assessment.get("evaluation_rounds", {})
    rounds = _require_mapping(rounds, "evaluation_rounds")
    for name, round_data in rounds.items():
        round_data = _require_mapping(round_data, f"evaluation_rounds.{name}")
        if "score" in round_data:
            _validate_score(round_data["score"], f"{name} score")
        for field in ("strengths", "weaknesses", "evidence"):
            if field in round_data:
                _string_list(round_data[field], f"{name}.{field}")

    for section_name in ("behavioral_assessment", "integrity_assessment"):
        section = assessment.get(section_name, {})
        section = _require_mapping(section, section_name)
        if "flags" in section:
            _string_list(section["flags"], f"{section_name}.flags")
        if "evidence" in section:
            _string_list(section["evidence"], f"{section_name}.evidence")

    recommendation = _require_mapping(
        assessment.get("day52_recommendation"), "day52_recommendation"
    )
    if "score" in recommendation:
        _validate_score(recommendation["score"], "recommendation score")
    if "confidence" in recommendation:
        _validate_score(recommendation["confidence"], "recommendation confidence")
    for field in ("reasons", "review_reasons"):
        if field in recommendation:
            _string_list(recommendation[field], f"day52_recommendation.{field}")
    return assessment


def build_hiring_report(
    assessment: dict[str, Any], config: dict[str, Any]
) -> dict[str, Any]:
    """Validate assessment evidence and assemble a recruiter-facing report."""
    assessment = _validate_assessment(assessment)
    config = _require_mapping(config, "Configuration")
    candidate = assessment["candidate"]
    input_rounds = assessment.get("evaluation_rounds", {})
    strength_threshold = _validate_score(
        config.get("strength_threshold", 80), "strength_threshold"
    )
    development_threshold = _validate_score(
        config.get("development_threshold", 60), "development_threshold"
    )

    rounds: dict[str, dict[str, Any]] = {}
    strengths: list[str] = []
    weaknesses: list[str] = []
    risk_indicators: list[dict[str, str]] = []
    completed_scores: list[float] = []

    for name in ROUND_NAMES:
        source = input_rounds.get(name)
        if source is None:
            source = {}
        status = source.get("status", "MISSING")
        if not isinstance(status, str):
            raise ReportInputError(f"{name}.status must be a string.")
        status = status.upper()

        result: dict[str, Any] = {
            "status": status,
            "summary": source.get("summary", ""),
            "strengths": source.get("strengths", []).copy(),
            "weaknesses": source.get("weaknesses", []).copy(),
            "evidence": source.get("evidence", []).copy(),
        }
        if "score" in source:
            score = _validate_score(source["score"], f"{name} score")
            result["score"] = score
            if status == "COMPLETE":
                completed_scores.append(score)
                if score >= strength_threshold:
                    strengths.append(
                        f"{name.replace('_', ' ').title()} score meets "
                        f"the strength threshold ({score:g}/100)."
                    )
                elif score < development_threshold:
                    weaknesses.append(
                        f"{name.replace('_', ' ').title()} score is below "
                        f"the development threshold ({score:g}/100)."
                    )
        rounds[name] = result
        strengths.extend(result["strengths"])
        weaknesses.extend(result["weaknesses"])
        if status != "COMPLETE":
            risk_indicators.append(
                {
                    "type": "incomplete_round",
                    "details": f"{name.replace('_', ' ').title()} status is {status}.",
                }
            )

    assessment_sections: dict[str, dict[str, Any]] = {}
    for section_name, label in (
        ("behavioral_assessment", "behavioral"),
        ("integrity_assessment", "integrity"),
    ):
        source = assessment.get(section_name, {})
        section = {
            "status": str(source.get("status", "MISSING")).upper(),
            "summary": source.get("summary", ""),
            "flags": source.get("flags", []).copy(),
            "evidence": source.get("evidence", []).copy(),
        }
        assessment_sections[label] = section
        if section["status"] != "COMPLETE":
            risk_indicators.append(
                {
                    "type": f"incomplete_{label}_assessment",
                    "details": f"{label.title()} assessment status is {section['status']}.",
                }
            )
        for flag in section["flags"]:
            risk_indicators.append(
                {"type": label, "details": flag}
            )

    recommendation = assessment["day52_recommendation"]
    reasons = recommendation.get("reasons", []).copy()
    review_reasons = recommendation.get("review_reasons", []).copy()
    requires_review = bool(risk_indicators)
    if requires_review:
        review_reasons.extend(
            indicator["details"] for indicator in risk_indicators
        )
    decision = (
        "HOLD_REVIEW"
        if requires_review
        else recommendation.get("decision", "HOLD_REVIEW")
    )
    unique_strengths = list(dict.fromkeys(strengths))
    unique_weaknesses = list(dict.fromkeys(weaknesses))

    return {
        "report_version": config.get("report_version", "unspecified"),
        "project_name": config.get("project_name", "Hiring System"),
        "report_title": config.get("report_title", "Hiring Intelligence Report"),
        "candidate_profile": {
            **candidate,
            "assessment_status": assessment.get("assessment_status", "UNKNOWN"),
        },
        "evaluation_summary": {
            "completed_scored_rounds": len(completed_scores),
            "overall_round_average": (
                round(sum(completed_scores) / len(completed_scores), 2)
                if completed_scores
                else None
            ),
            "rounds": rounds,
        },
        "candidate_insights": {
            "strengths": unique_strengths,
            "weaknesses": unique_weaknesses,
        },
        "behavioral_assessment": assessment_sections["behavioral"],
        "integrity_assessment": assessment_sections["integrity"],
        "risk_indicators": risk_indicators,
        "final_recommendation": {
            "decision": decision,
            "score": recommendation.get("score"),
            "confidence": recommendation.get("confidence"),
            "confidence_interpretation": recommendation.get(
                "confidence_interpretation", ""
            ),
            "reasons": reasons,
            "review_reasons": review_reasons,
            "human_review_required": True,
            "recommendation_only": True,
            "disclaimer": ADVISORY_DISCLAIMER,
        },
    }


def render_markdown(report: dict[str, Any]) -> str:
    """Render a completed report as Markdown."""
    candidate = report["candidate_profile"]
    summary = report["evaluation_summary"]
    recommendation = report["final_recommendation"]
    lines = [
        f"# {report['report_title']}",
        "",
        "## Candidate Profile",
        "",
        f"- **Candidate ID:** {candidate['candidate_id']}",
        f"- **Name:** {candidate['name']}",
        f"- **Target role:** {candidate['target_role']}",
        f"- **Assessment status:** {candidate['assessment_status']}",
        "",
        "## Executive Summary",
        "",
        f"- **Completed scored rounds:** {summary['completed_scored_rounds']}",
        f"- **Overall round average:** {summary['overall_round_average']}",
        f"- **Final recommendation:** {recommendation['decision']}",
        "",
        "## Evaluation Results",
        "",
        "| Round | Status | Score | Summary |",
        "|---|---|---:|---|",
    ]
    for name, result in summary["rounds"].items():
        score = result.get("score", "N/A")
        lines.append(
            f"| {name.replace('_', ' ').title()} | {result['status']} | "
            f"{score} | {result['summary']} |"
        )

    lines.extend(["", "## Strengths", ""])
    lines.extend(
        f"- {item}" for item in report["candidate_insights"]["strengths"]
    )
    if not report["candidate_insights"]["strengths"]:
        lines.append("- No strengths were supplied.")
    lines.extend(["", "## Weaknesses and Development Areas", ""])
    lines.extend(
        f"- {item}" for item in report["candidate_insights"]["weaknesses"]
    )
    if not report["candidate_insights"]["weaknesses"]:
        lines.append("- No development areas were supplied.")

    lines.extend(["", "## Risk Indicators", ""])
    for indicator in report["risk_indicators"]:
        lines.append(f"- **{indicator['type']}:** {indicator['details']}")
    if not report["risk_indicators"]:
        lines.append("- No unresolved risk indicators were recorded.")

    lines.extend(
        [
            "",
            "## Final Recommendation",
            "",
            f"- **Decision:** {recommendation['decision']}",
            f"- **Unified score:** {recommendation['score']}",
            f"- **Confidence:** {recommendation['confidence']}",
            f"- **Human review required:** {recommendation['human_review_required']}",
            "",
        ]
    )
    if recommendation["reasons"]:
        lines.append("Reasons:")
        lines.extend(f"- {reason}" for reason in recommendation["reasons"])
    if recommendation["review_reasons"]:
        lines.extend(["", "Review reasons:"])
        lines.extend(
            f"- {reason}" for reason in recommendation["review_reasons"]
        )
    lines.extend(
        [
            "",
            "## Review Checklist",
            "",
            "- Verify the underlying assessment evidence.",
            "- Resolve any listed risk indicators before proceeding.",
            "",
            f"> {recommendation['disclaimer']}",
            "",
        ]
    )
    return "\n".join(lines)


def save_report(
    report: dict[str, Any], output_dir: str | Path
) -> tuple[Path, Path]:
    """Write the JSON and Markdown exports and return their paths."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    json_path = output_path / "hiring_intelligence_report.json"
    markdown_path = output_path / "hiring_intelligence_report.md"

    with json_path.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2, ensure_ascii=False)
        file.write("\n")
    markdown_path.write_text(render_markdown(report), encoding="utf-8")
    return json_path, markdown_path
