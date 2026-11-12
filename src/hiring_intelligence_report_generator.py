"""Day 53: Comprehensive Hiring Intelligence Report Generator."""

import json
from typing import Any
try:
    from . import database
except ImportError:
    from src import database


ADVISORY_DISCLAIMER: str = (
    "This report is advisory only. A qualified human reviewer must verify "
    "the underlying evidence before making any employment decision."
)


def generate_candidate_hiring_report(
    candidate_id: str,
    recruiter_id: str | None = None,
    save_to_db: bool = True,
) -> dict[str, Any]:
    """
    Compiles actual persisted candidate evaluations from all 5 rounds,
    compliance, integrity, and behavioral subsystems into a 15-section report.
    """
    candidate = database.get_candidate(candidate_id)
    if not candidate:
        raise ValueError(f"Candidate {candidate_id} not found.")

    opening_id = candidate.get("opening_id", "")
    opening = database.get_opening(opening_id) if opening_id else None
    target_role = (
        opening.get("title")
        if opening
        else candidate.get("target_role") or "Software Engineer"
    )

    # 1. ATS / Resume Data
    ats_score = candidate.get("score")
    matched_skills = candidate.get("extracted_skills") or []
    missing_skills = candidate.get("missing_skills") or []
    resume_profile = candidate.get("extracted_profile") or {}
    ats_summary = {
        "score": float(ats_score) if ats_score is not None else None,
        "classification": candidate.get("classification", "NOT_EVALUATED"),
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "years_experience": resume_profile.get("years_experience"),
        "education": resume_profile.get("education", []),
        "status": "COMPLETE" if ats_score is not None else "MISSING",
    }

    # 2. Eligibility
    eligibility = database.get_candidate_eligibility_evaluation(candidate_id)

    # 3. Screening Evaluation
    screening_sessions = database.list_screening_sessions_for_candidate(candidate_id)
    screening_score = None
    screening_status = "MISSING"
    screening_notes = []
    if screening_sessions:
        s_sess = screening_sessions[0]
        screening_score = s_sess.get("overall_score")
        screening_status = s_sess.get("status", "COMPLETE")
        screening_notes.append(s_sess.get("summary_notes") or "Screening completed.")
    screening_summary = {
        "score": float(screening_score) if screening_score is not None else None,
        "status": screening_status,
        "notes": screening_notes,
    }

    # 4. HR Interview
    hr_interviews = database.list_hr_interviews(candidate_id)
    hr_score = None
    hr_status = "MISSING"
    hr_comm_summary = None
    if hr_interviews:
        hr_int = hr_interviews[0]
        hr_score = hr_int.get("overall_score")
        hr_status = hr_int.get("status", "COMPLETED")
        comm_evals = database.get_hr_communication_evaluations(hr_int["interview_id"])
        if comm_evals:
            hr_comm_summary = {
                "clarity": comm_evals[0].get("clarity_score"),
                "pacing": comm_evals[0].get("pacing_score"),
                "structure": comm_evals[0].get("structure_score"),
            }
    hr_summary = {
        "score": float(hr_score) if hr_score is not None else None,
        "status": hr_status,
        "communication_evaluation": hr_comm_summary,
    }

    # 5. Technical Interview
    tech_sessions = database.list_technical_interview_sessions(candidate_id)
    tech_score = None
    tech_status = "MISSING"
    tech_depth_summary = {"deep": 0, "moderate": 0, "shallow": 0}
    if tech_sessions:
        t_sess = tech_sessions[0]
        tech_status = t_sess.get("status", "COMPLETED")
        if t_sess.get("overall_score"):
            tech_score = float(t_sess["overall_score"])
        responses = database.list_technical_interview_responses(t_sess["session_id"])
        if responses:
            norm_scores = [
                float(r["score"]) for r in responses if r.get("score") is not None
            ] or [
                float(r["normalized_score"]) for r in responses if r.get("normalized_score") is not None
            ]
            if norm_scores and tech_score is None:
                tech_score = round(sum(norm_scores) / len(norm_scores), 2)
            for r in responses:
                d = r.get("depth_level") or r.get("depth_classification", "moderate")
                if d in tech_depth_summary:
                    tech_depth_summary[d] += 1
    technical_summary = {
        "score": tech_score,
        "status": tech_status,
        "depth_breakdown": tech_depth_summary,
    }

    # 6. Machine Test
    machine_assignments = database.list_machine_test_assignments(candidate_id)
    machine_score = None
    machine_status = "MISSING"
    machine_rubric = {}
    if machine_assignments:
        m_assign = machine_assignments[0]
        machine_status = m_assign.get("status", "ASSIGNED")
        sub = database.get_machine_test_submission(m_assign["test_id"])
        if sub:
            machine_score = sub.get("total_score")
            machine_rubric = {
                "correctness": sub.get("correctness_score"),
                "efficiency": sub.get("efficiency_score"),
                "code_quality": sub.get("code_quality_score"),
                "problem_solving": sub.get("problem_solving_score"),
                "time_management": sub.get("time_management_score"),
            }
    machine_test_summary = {
        "score": float(machine_score) if machine_score is not None else None,
        "status": machine_status,
        "rubric_scores": machine_rubric,
    }

    # 7. Behavioral Observations (Consented)
    behav_records = database.get_candidate_behavioral_records(candidate_id)
    behav_summary = {
        "consent_recorded": bool(behav_records and behav_records[0].get("consent_recorded")),
        "consistency_index": behav_records[0].get("signal_consistency_index") if behav_records else None,
        "description": behav_records[0].get("signal_description") if behav_records else "No consented observations recorded.",
        "disclaimer": ADVISORY_DISCLAIMER,
    }

    # 8. Integrity Flags (Consented)
    integrity_records = database.get_candidate_integrity_records(candidate_id)
    integrity_flags = []
    integrity_risk = "LOW"
    if integrity_records:
        r = integrity_records[0]
        integrity_risk = r.get("risk_level", "LOW")
        integrity_flags = r.get("review_flags", [])
    integrity_summary = {
        "risk_level": integrity_risk,
        "review_flags": integrity_flags,
        "human_review_required": integrity_risk in ("MODERATE", "HIGH") or len(integrity_flags) > 0,
        "automatic_rejection_applied": False,
    }

    # 9. Cross-Round Unified Fit
    cross_evals = database.list_cross_round_evaluations(candidate_id)
    unified_fit = None
    effective_weights = {}
    missing_rounds = []
    anomalies = []
    if cross_evals:
        last_eval = cross_evals[0]
        unified_fit = last_eval.get("hiring_fit_percentage")
        effective_weights = last_eval.get("effective_weights", {})
        missing_rounds = last_eval.get("missing_rounds", [])
        anomalies = last_eval.get("anomalies", [])
    else:
        # Fallback calculation from available rounds
        round_scores = {
            "ats": ats_score,
            "screening": screening_score,
            "hr_interview": hr_score,
            "technical_interview": tech_score,
            "machine_test": machine_score,
        }
        completed = {k: v for k, v in round_scores.items() if v is not None}
        missing_rounds = [k for k, v in round_scores.items() if v is None]
        if completed:
            unified_fit = round(sum(completed.values()) / len(completed), 2)

    # 10. Final Recommendation
    final_recs = database.list_final_recommendations(candidate_id)
    final_rec = final_recs[0] if final_recs else None
    recommendation_summary = {
        "decision": final_rec["decision"] if final_rec else ("SELECTED" if (unified_fit or 0) >= 80 and not missing_rounds else "HOLD_REVIEW"),
        "confidence": final_rec["confidence"] if final_rec else round(max(0.2, (5 - len(missing_rounds)) / 5.0), 2),
        "confidence_interpretation": "Evidence completeness indicator; not a probability of job success.",
        "reasons": final_rec["reasons"] if final_rec else ["Automated synthesis of completed assessment rounds."],
        "recruiter_decision": final_rec["recruiter_decision"] if final_rec else "PENDING_REVIEW",
        "recruiter_notes": final_rec.get("recruiter_notes") if final_rec else None,
        "disclaimer": ADVISORY_DISCLAIMER,
    }

    # Strengths & Weaknesses synthesis
    strengths = []
    weaknesses = []
    if ats_score is not None and ats_score >= 80:
        strengths.append(f"Strong resume profile alignment ({ats_score:.1f}% ATS score).")
    if matched_skills:
        strengths.append(f"Demonstrated verified competencies in: {', '.join(matched_skills[:5])}.")
    if tech_score is not None and tech_score >= 80:
        strengths.append(f"Strong technical architecture & problem-solving performance ({tech_score:.1f}/100).")
    if machine_score is not None and machine_score >= 80:
        strengths.append(f"High-quality machine test implementation and efficiency ({machine_score:.1f}/100).")

    if missing_skills:
        weaknesses.append(f"Skill gaps identified against job description: {', '.join(missing_skills[:5])}.")
    if tech_depth_summary["shallow"] > 0:
        weaknesses.append(f"Exhibited shallow depth on {tech_depth_summary['shallow']} technical questions.")
    if machine_score is not None and machine_score < 65:
        weaknesses.append(f"Machine test performance ({machine_score:.1f}/100) below target benchmark.")

    # Risk Indicators
    risk_indicators = []
    for m in missing_rounds:
        risk_indicators.append({"type": "missing_round", "details": f"Evaluation round '{m}' has not been completed."})
    for a in anomalies:
        risk_indicators.append({"type": "anomaly", "details": str(a)})
    for f in integrity_flags:
        risk_indicators.append({"type": "integrity", "details": str(f)})

    report_payload: dict[str, Any] = {
        "report_title": "ZecPath Comprehensive Hiring Intelligence Report",
        "report_version": "1.0",
        "candidate_id": candidate_id,
        "candidate_name": candidate.get("name", "Unknown Candidate"),
        "candidate_email": candidate.get("email", ""),
        "target_role": target_role,
        "opening_id": opening_id,
        "job_title": opening.get("title") if opening else target_role,
        "unified_hiring_fit_score": unified_fit,
        "evaluation_summary": {
            "ats": ats_summary,
            "eligibility": eligibility,
            "screening": screening_summary,
            "hr_interview": hr_summary,
            "technical_interview": technical_summary,
            "machine_test": machine_test_summary,
            "behavioral": behav_summary,
            "integrity": integrity_summary,
        },
        "strengths": strengths,
        "weaknesses_and_skill_gaps": weaknesses,
        "missing_evaluation_evidence": missing_rounds,
        "risk_indicators": risk_indicators,
        "effective_weights": effective_weights,
        "final_recommendation": recommendation_summary,
        "recruiter_decision_workflow": {
            "status": recommendation_summary["recruiter_decision"],
            "notes": recommendation_summary["recruiter_notes"],
            "governance": "Human recruiter approval is mandatory prior to candidate status changes.",
        },
        "disclaimer": ADVISORY_DISCLAIMER,
    }

    markdown_content = render_report_markdown(report_payload)
    html_content = render_report_html(report_payload)

    if save_to_db:
        saved = database.save_hiring_intelligence_report(
            candidate_id=candidate_id,
            opening_id=opening_id,
            report_json=report_payload,
            markdown_content=markdown_content,
            html_content=html_content,
            created_by_recruiter_id=recruiter_id,
        )
        report_payload["report_id"] = saved["report_id"]
        report_payload["version"] = saved["version"]
        report_payload["created_at"] = saved["created_at"]

    return report_payload


def render_report_markdown(report: dict[str, Any]) -> str:
    """Renders structured report payload to readable Markdown format."""
    lines = [
        f"# {report['report_title']}",
        f"**Candidate:** {report['candidate_name']} ({report['candidate_id']})",
        f"**Target Role:** {report['target_role']} | **Job Opening:** {report['job_title']} ({report['opening_id']})",
        f"**Unified Hiring Fit:** {report.get('unified_hiring_fit_score', 'N/A')}%",
        f"**Final AI Recommendation:** {report['final_recommendation']['decision']}",
        f"**Recruiter Decision:** {report['final_recommendation']['recruiter_decision']}",
        "",
        "---",
        "",
        "## 1. Executive Summary & Recommendation",
        f"- **Recommendation:** {report['final_recommendation']['decision']}",
        f"- **Confidence:** {report['final_recommendation']['confidence']} ({report['final_recommendation']['confidence_interpretation']})",
        f"- **Recruiter Review Status:** {report['final_recommendation']['recruiter_decision']}",
        "",
        "### Recommendation Rationale:",
    ]
    for reason in report["final_recommendation"]["reasons"]:
        lines.append(f"- {reason}")

    lines.extend([
        "",
        "## 2. Strengths",
    ])
    if report["strengths"]:
        for s in report["strengths"]:
            lines.append(f"- {s}")
    else:
        lines.append("- No distinct strengths recorded.")

    lines.extend([
        "",
        "## 3. Weaknesses & Skill Gaps",
    ])
    if report["weaknesses_and_skill_gaps"]:
        for w in report["weaknesses_and_skill_gaps"]:
            lines.append(f"- {w}")
    else:
        lines.append("- No substantial skill gaps recorded.")

    lines.extend([
        "",
        "## 4. Evaluation Breakdown by Round",
        f"- **Resume ATS Score:** {report['evaluation_summary']['ats']['score']}%",
        f"- **HR Screening Score:** {report['evaluation_summary']['screening']['score']}",
        f"- **HR Interview Score:** {report['evaluation_summary']['hr_interview']['score']}",
        f"- **Technical Interview Score:** {report['evaluation_summary']['technical_interview']['score']}",
        f"- **Machine Test Score:** {report['evaluation_summary']['machine_test']['score']}",
        "",
        "## 5. Integrity & Behavioral Advisory",
        f"- **Integrity Risk Level:** {report['evaluation_summary']['integrity']['risk_level']}",
        f"- **Behavioral Consistency Index:** {report['evaluation_summary']['behavioral']['consistency_index']}",
        "",
        "## 6. Risk Indicators & Incomplete Rounds",
    ])
    if report["risk_indicators"]:
        for r in report["risk_indicators"]:
            lines.append(f"- **{r['type'].upper()}**: {r['details']}")
    else:
        lines.append("- No critical risk factors identified.")

    lines.extend([
        "",
        "---",
        f"*{report['disclaimer']}*",
    ])
    return "\n".join(lines)


def render_report_html(report: dict[str, Any]) -> str:
    """Renders structured report payload to polished, export-ready HTML format."""
    fit_score = report.get("unified_hiring_fit_score")
    fit_str = f"{fit_score:.1f}%" if fit_score is not None else "Pending"
    decision = report["final_recommendation"]["decision"]
    decision_color = "#10b981" if decision == "SELECTED" else ("#f59e0b" if decision == "HOLD_REVIEW" else "#ef4444")

    strengths_li = "".join(f"<li>{s}</li>" for s in report["strengths"]) or "<li>No distinct strengths recorded.</li>"
    weaknesses_li = "".join(f"<li>{w}</li>" for w in report["weaknesses_and_skill_gaps"]) or "<li>No critical gaps detected.</li>"
    risks_li = "".join(f"<li><strong>{r['type'].upper()}</strong>: {r['details']}</li>" for r in report["risk_indicators"]) or "<li>Zero risk alerts triggered.</li>"
    reasons_li = "".join(f"<li>{r}</li>" for r in report["final_recommendation"]["reasons"])

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{report['report_title']} - {report['candidate_name']}</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #1f2937; margin: 0; padding: 40px; background: #f9fafb; }}
  .container {{ max-width: 900px; margin: 0 auto; background: #ffffff; padding: 40px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.06); border: 1px solid #e5e7eb; }}
  .header {{ border-bottom: 2px solid #e5e7eb; padding-bottom: 20px; margin-bottom: 30px; }}
  .badge {{ display: inline-block; padding: 4px 12px; border-radius: 9999px; font-weight: 600; font-size: 0.875rem; color: #fff; background: {decision_color}; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
  .card {{ background: #f3f4f6; padding: 16px; border-radius: 8px; }}
  .card-title {{ font-size: 0.75rem; text-transform: uppercase; color: #6b7280; font-weight: 700; margin-bottom: 6px; }}
  .card-value {{ font-size: 1.5rem; font-weight: 800; color: #111827; }}
  h1 {{ margin: 0; font-size: 1.75rem; color: #111827; }}
  h2 {{ font-size: 1.25rem; border-bottom: 1px solid #e5e7eb; padding-bottom: 8px; margin-top: 30px; color: #111827; }}
  ul {{ padding-left: 20px; }}
  li {{ margin-bottom: 6px; }}
  .footer {{ margin-top: 40px; padding-top: 20px; border-top: 1px solid #e5e7eb; font-size: 0.8125rem; color: #6b7280; font-style: italic; }}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <div style="display:flex; justify-content:space-between; align-items:center;">
      <div>
        <h1>{report['report_title']}</h1>
        <p style="margin:4px 0 0 0; color:#6b7280;">Target: <strong>{report['target_role']}</strong> | Opening: <strong>{report['job_title']}</strong></p>
      </div>
      <div><span class="badge">{decision}</span></div>
    </div>
  </div>

  <div class="grid">
    <div class="card">
      <div class="card-title">Candidate</div>
      <div class="card-value" style="font-size:1.125rem;">{report['candidate_name']}</div>
      <small style="color:#6b7280;">{report['candidate_email']}</small>
    </div>
    <div class="card">
      <div class="card-title">Unified Fit Score</div>
      <div class="card-value">{fit_str}</div>
    </div>
    <div class="card">
      <div class="card-title">Evidence Confidence</div>
      <div class="card-value">{int(report['final_recommendation']['confidence'] * 100)}%</div>
    </div>
    <div class="card">
      <div class="card-title">Recruiter Decision</div>
      <div class="card-value" style="font-size:1.125rem;">{report['final_recommendation']['recruiter_decision']}</div>
    </div>
  </div>

  <h2>1. AI Recommendation & Rationale</h2>
  <ul>{reasons_li}</ul>

  <h2>2. Identified Strengths</h2>
  <ul style="color:#065f46;">{strengths_li}</ul>

  <h2>3. Weaknesses & Skill Gaps</h2>
  <ul style="color:#991b1b;">{weaknesses_li}</ul>

  <h2>4. Multi-Round Evaluation Summary</h2>
  <div class="grid">
    <div class="card"><div class="card-title">ATS Resume</div><div class="card-value">{report['evaluation_summary']['ats']['score'] or 'N/A'}%</div></div>
    <div class="card"><div class="card-title">HR Screening</div><div class="card-value">{report['evaluation_summary']['screening']['score'] or 'N/A'}</div></div>
    <div class="card"><div class="card-title">HR Interview</div><div class="card-value">{report['evaluation_summary']['hr_interview']['score'] or 'N/A'}</div></div>
    <div class="card"><div class="card-title">Technical Interview</div><div class="card-value">{report['evaluation_summary']['technical_interview']['score'] or 'N/A'}</div></div>
    <div class="card"><div class="card-title">Machine Test</div><div class="card-value">{report['evaluation_summary']['machine_test']['score'] or 'N/A'}</div></div>
  </div>

  <h2>5. Risk Indicators & Auxiliary Alerts</h2>
  <ul>{risks_li}</ul>

  <div class="footer">
    {report['disclaimer']}
  </div>
</div>
</body>
</html>"""
