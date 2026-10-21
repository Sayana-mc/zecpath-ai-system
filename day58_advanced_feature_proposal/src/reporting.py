"""Generate a proposal report from configuration and prototype results."""
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path


def atomic_write_json(path, payload):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(payload, stream, indent=2, ensure_ascii=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp_name, path)
    except Exception:
        try:
            os.unlink(temp_name)
        except OSError:
            pass
        raise


def build_proposal_report(roadmap, features, coaching_plan):
    return {
        "schema_version": "1.0",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "project": roadmap.get("project", "Zecpath AI Hiring System"),
        "day": 58,
        "status": "PROPOSAL_AND_LOCAL_PROTOTYPE",
        "feature_count": len(features),
        "roadmap_phase_count": len(roadmap["phases"]),
        "principles": roadmap["principles"],
        "features": features,
        "roadmap": roadmap["phases"],
        "coaching_prototype": coaching_plan,
        "limitations": [
            "The coaching prototype uses transparent rules and supplied skill lists; it is not a trained AI model.",
            "Video analysis is proposed as an optional consent-based workflow, not implemented here.",
            "Emotion or personality inference is excluded from hiring decisions.",
            "The roadmap is a proposal and requires privacy, security, legal, accessibility, and stakeholder review."
        ]
    }


def write_markdown(path, report):
    lines = [
        "# Day 58 — Advanced Feature Proposal", "",
        f"**Project:** {report['project']}",
        f"**Generated (UTC):** {report['generated_at_utc']}",
        f"**Status:** {report['status']}", "",
        "## Executive Summary", "",
        "This proposal describes future features for candidate coaching, real-time practice feedback, interview analytics, optional consent-based video review, and scaling. It includes a small rule-based coaching prototype.", "",
        "## Safety and Governance Principles", "",
        f"- Human review required: **{report['principles']['human_review_required']}**",
        f"- Automatic rejection enabled: **{report['principles']['automatic_rejection_enabled']}**",
        f"- Emotion inference for hiring enabled: **{report['principles']['emotion_inference_for_hiring_enabled']}**",
        f"- Video analysis requires explicit consent: **{report['principles']['video_analysis_requires_explicit_consent']}**", "",
        "## Proposed Features", ""
    ]
    for feature in report["features"]:
        lines += [f"### {feature['id']} — {feature['name']}", "", feature["description"], "", f"- Priority: {feature['priority']}", f"- Status: {feature['status']}", "- Guardrails:"]
        lines += [f"  - {guardrail}" for guardrail in feature["guardrails"]]
        lines += ["- Acceptance criteria:"]
        lines += [f"  - {criterion}" for criterion in feature["acceptance_criteria"]]
        lines.append("")
    lines += ["## Roadmap", ""]
    for phase in report["roadmap"]:
        lines += [f"### {phase['id']} — {phase['name']}", "", f"**Timeline:** {phase['timeline']} | **Priority:** {phase['priority']}", "", "Features:"]
        lines += [f"- {item}" for item in phase["features"]]
        lines += ["Exit criteria:"]
        lines += [f"- {item}" for item in phase["exit_criteria"]]
        lines.append("")
    lines += ["## Coaching Prototype Summary", "", report["coaching_prototype"]["summary"], "", "Suggested practice actions:"]
    if report["coaching_prototype"]["skills_to_practice"]:
        for item in report["coaching_prototype"]["skills_to_practice"]:
            lines.append(f"- **{item['skill']}**: {item['suggestion']}")
    else:
        lines.append("- No skill gaps were identified from the supplied inputs.")
    lines += ["", "## Limitations", ""]
    lines += [f"- {item}" for item in report["limitations"]]
    lines += ["", "## Conclusion", "", "The proposal prioritizes transparent candidate coaching and structured interview analytics before more complex integrations. Video processing should be optional and consent-based. Emotion and personality inference are excluded from hiring decisions. Production implementation requires appropriate technical, privacy, security, accessibility, and stakeholder reviews.", ""]
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text("\n".join(lines), encoding="utf-8")
