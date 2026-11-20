"""Day 53: Comprehensive Hiring Intelligence Report Generator with HTML, Markdown, and PDF Export."""

from datetime import datetime, timezone
from html import escape
from typing import Any

try:
    from . import database
except ImportError:
    from src import database


ADVISORY_DISCLAIMER: str = (
    "CONFIDENTIAL — DECISION SUPPORT ONLY: This report is advisory only and generated "
    "from persisted assessment records. A qualified human reviewer must verify the "
    "underlying evidence before making any employment decision."
)


def _format_confidence_pct(raw_conf: Any) -> int:
    if raw_conf is None:
        return 0
    val = float(raw_conf)
    if val <= 1.0:
        return int(round(val * 100.0))
    return int(round(min(100.0, max(0.0, val))))


def generate_candidate_hiring_report(
    candidate_id: str,
    recruiter_id: str | None = None,
    save_to_db: bool = True,
) -> dict[str, Any]:
    """
    Compiles actual persisted candidate evaluations from all 5 rounds,
    eligibility, compliance, integrity, and behavioral subsystems into a 14-section report.
    Never invents scores for missing rounds.
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
    score_evidence = candidate.get("score_evidence") or {}
    if isinstance(score_evidence, str):
        score_evidence = {}
    matched_skills = (
        score_evidence.get("matched_required_skills")
        or candidate.get("extracted_skills")
        or candidate.get("skills")
        or []
    )
    missing_skills = (
        score_evidence.get("missing_required_skills")
        or candidate.get("missing_skills")
        or []
    )
    resume_profile = candidate.get("resume_data") or candidate.get("extracted_profile") or {}
    ats_summary = {
        "score": round(float(ats_score), 2) if ats_score is not None else None,
        "classification": score_evidence.get("classification") or candidate.get("classification") or ("EVALUATED" if ats_score is not None else "NOT_EVALUATED"),
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "years_experience": resume_profile.get("experience_years") or resume_profile.get("years_experience"),
        "education": resume_profile.get("education", []),
        "status": "COMPLETE" if ats_score is not None else "MISSING",
    }

    # 2. Eligibility
    eligibility = database.get_candidate_eligibility_evaluation(candidate_id, opening_id or None)

    # 3. Screening Evaluation
    screening_sessions = database.list_screening_sessions_for_candidate(candidate_id)
    screening_score = None
    screening_status = "MISSING"
    screening_notes = []
    if screening_sessions:
        s_sess = screening_sessions[0]
        screening_status = s_sess.get("status", "COMPLETE")
        agg = database.get_screening_aggregate_score(s_sess["session_id"])
        reports = database.list_screening_reports_full(s_sess["session_id"])
        if agg and agg.get("overall_score") is not None:
            screening_score = float(agg["overall_score"])
        elif reports and reports[0].get("report_json", {}).get("overall_score") is not None:
            screening_score = float(reports[0]["report_json"]["overall_score"])
        elif s_sess.get("overall_score") is not None:
            screening_score = float(s_sess["overall_score"])
        if s_sess.get("summary_notes"):
            screening_notes.append(s_sess["summary_notes"])
        elif screening_score is not None:
            screening_notes.append(f"Screening aggregate score recorded ({screening_score:.1f}/100).")
    screening_summary = {
        "score": round(float(screening_score), 2) if screening_score is not None else None,
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
        hr_status = hr_int.get("status", "COMPLETED")
        hr_sc = database.get_hr_interview_score(hr_int["interview_id"])
        if hr_sc and hr_sc.get("overall_hr_score") is not None:
            hr_score = float(hr_sc["overall_hr_score"])
        elif hr_int.get("overall_score") is not None:
            hr_score = float(hr_int["overall_score"])
        comm_evals = database.get_hr_communication_evaluations(hr_int["interview_id"])
        if comm_evals:
            hr_comm_summary = {
                "clarity": comm_evals[0].get("clarity_score"),
                "fluency": comm_evals[0].get("fluency_score"),
                "structure": comm_evals[0].get("structure_score"),
                "total_communication": comm_evals[0].get("total_communication_score"),
            }
    hr_summary = {
        "score": round(float(hr_score), 2) if hr_score is not None else None,
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
        if t_sess.get("overall_score") is not None and float(t_sess["overall_score"]) > 0:
            tech_score = round(float(t_sess["overall_score"]), 2)
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
        assign_key = m_assign.get("assignment_id") or m_assign.get("test_id")
        machine_status = m_assign.get("status", "ASSIGNED")
        subs = database.list_machine_test_submissions(assign_key) if assign_key else []
        sub = subs[0] if subs else (database.get_machine_test_submission(assign_key) if assign_key else None)
        if sub:
            machine_score = round(float(sub["total_score"]), 2) if sub.get("total_score") is not None else None
            r_scores = sub.get("rubric_scores") or {}
            machine_rubric = {
                "correctness": r_scores.get("correctness", sub.get("correctness_score")),
                "efficiency": r_scores.get("efficiency", sub.get("efficiency_score")),
                "code_quality": r_scores.get("code_quality", sub.get("code_quality_score")),
                "problem_solving": r_scores.get("problem_solving", sub.get("problem_solving_score")),
                "time_management": r_scores.get("time_management", sub.get("time_management_score")),
            }
    machine_test_summary = {
        "score": machine_score,
        "status": machine_status,
        "rubric_scores": machine_rubric,
    }

    # 7. Behavioral Observations (Consented)
    behav_records = database.get_candidate_behavioral_records(candidate_id)
    behav_latest = behav_records[0] if behav_records else None
    behav_summary = {
        "consent_recorded": bool(behav_latest and (behav_latest.get("has_consent") or behav_latest.get("consent_recorded"))),
        "consistency_index": (
            behav_latest.get("consistency_index")
            if behav_latest and behav_latest.get("consistency_index") is not None
            else (behav_latest.get("signal_consistency_index") if behav_latest else None)
        ),
        "observations": behav_latest.get("observations", []) if behav_latest else [],
        "description": (
            f"Recorded {len(behav_latest.get('observations', []))} non-invasive operational indicator(s)."
            if behav_latest
            else "No consented observations recorded."
        ),
        "disclaimer": ADVISORY_DISCLAIMER,
    }

    # 8. Integrity Flags (Consented)
    integrity_records = database.get_candidate_integrity_records(candidate_id)
    integrity_flags = []
    integrity_risk = "LOW"
    integrity_human_review = False
    if integrity_records:
        r = integrity_records[0]
        integrity_risk = r.get("risk_level", "LOW")
        integrity_flags = r.get("review_flags", [])
        integrity_human_review = bool(r.get("requires_human_review"))
    integrity_summary = {
        "risk_level": integrity_risk,
        "review_flags": integrity_flags,
        "human_review_required": integrity_human_review or integrity_risk in ("MODERATE", "HIGH") or len(integrity_flags) > 0,
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
        effective_weights = last_eval.get("normalized_weights") or last_eval.get("effective_weights") or {}
        missing_rounds = last_eval.get("missing_rounds", [])
        anomalies = last_eval.get("anomalies", [])
    else:
        round_scores = {
            "ats": ats_score,
            "screening": screening_score,
            "hr_interview": hr_score,
            "technical_interview": tech_score,
            "machine_test": machine_score,
        }
        completed = {k: float(v) for k, v in round_scores.items() if v is not None}
        missing_rounds = [k for k, v in round_scores.items() if v is None]
        if completed:
            unified_fit = round(sum(completed.values()) / len(completed), 2)

    # 10. Final Recommendation
    final_recs = database.list_final_recommendations(candidate_id)
    final_rec = final_recs[0] if final_recs else None
    raw_conf = final_rec["confidence"] if final_rec else round(max(0.2, (5 - len(missing_rounds)) / 5.0) * 100.0, 2)
    recommendation_summary = {
        "recommendation_id": final_rec["recommendation_id"] if final_rec else None,
        "decision": final_rec["decision"] if final_rec else ("SELECTED" if (unified_fit or 0) >= 80 and not missing_rounds else "HOLD_REVIEW"),
        "confidence": raw_conf,
        "confidence_percent": _format_confidence_pct(raw_conf),
        "confidence_interpretation": "Evidence completeness indicator; not a probability of job success.",
        "reasons": final_rec["reasons"] if final_rec else ["Automated synthesis of completed assessment rounds."],
        "reason_codes": final_rec.get("reason_codes", []) if final_rec else [],
        "recruiter_decision": final_rec["recruiter_decision"] if final_rec else "PENDING_REVIEW",
        "recruiter_notes": final_rec.get("recruiter_notes") if final_rec else None,
        "disclaimer": ADVISORY_DISCLAIMER,
    }

    # Strengths & Weaknesses synthesis
    strengths = list(final_rec.get("strengths", [])) if final_rec else []
    weaknesses = list(final_rec.get("weaknesses", [])) if final_rec else []
    if not strengths:
        if ats_score is not None and ats_score >= 80:
            strengths.append(f"Strong resume profile alignment ({ats_score:.1f}% ATS score).")
        if matched_skills:
            strengths.append(f"Demonstrated verified competencies in: {', '.join(matched_skills[:5])}.")
        if tech_score is not None and tech_score >= 80:
            strengths.append(f"Strong technical architecture & problem-solving performance ({tech_score:.1f}/100).")
        if machine_score is not None and machine_score >= 80:
            strengths.append(f"High-quality machine test implementation and efficiency ({machine_score:.1f}/100).")
    if not weaknesses:
        if missing_skills:
            weaknesses.append(f"Skill gaps identified against job description: {', '.join(missing_skills[:5])}.")
        if tech_depth_summary["shallow"] > 0:
            weaknesses.append(f"Exhibited shallow depth on {tech_depth_summary['shallow']} technical questions.")
        if machine_score is not None and machine_score < 65:
            weaknesses.append(f"Machine test performance ({machine_score:.1f}/100) below target benchmark.")

    # Risk Indicators
    risk_indicators = []
    if eligibility and eligibility.get("status") in ("REJECTED", "REVIEW"):
        risk_indicators.append({
            "type": "eligibility",
            "details": f"Eligibility status is {eligibility['status']}: {eligibility.get('decision_explanation', '')}",
        })
    for m in missing_rounds:
        risk_indicators.append({"type": "missing_round", "details": f"Evaluation round '{m}' has not been completed."})
    for a in anomalies:
        risk_indicators.append({"type": "anomaly", "details": str(a)})
    for f in integrity_flags:
        risk_indicators.append({"type": "integrity", "details": str(f)})

    generated_at = datetime.now(timezone.utc).isoformat()
    report_payload: dict[str, Any] = {
        "report_title": "ZecPath Comprehensive Hiring Intelligence Report",
        "report_version": "1.1",
        "generated_at": generated_at,
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
        # Re-render HTML/Markdown with persisted report_id and version
        markdown_content = render_report_markdown(report_payload)
        html_content = render_report_html(report_payload)
        with database._connection() as conn:
            conn.execute(
                "UPDATE hiring_intelligence_reports SET markdown_content = ?, html_content = ? WHERE report_id = ?",
                (markdown_content, html_content, saved["report_id"]),
            )

    return report_payload


def render_report_markdown(report: dict[str, Any]) -> str:
    """Renders structured report payload to readable Markdown format."""
    conf_pct = _format_confidence_pct(report["final_recommendation"].get("confidence"))
    lines = [
        f"# {report['report_title']}",
        f"**Report ID:** {report.get('report_id', 'Preview')} | **Version:** v{report.get('version', 1)} | **Generated:** {report.get('created_at', report.get('generated_at', ''))}",
        f"**Candidate:** {report['candidate_name']} ({report['candidate_id']})",
        f"**Target Role:** {report['target_role']} | **Job Opening:** {report['job_title']} ({report['opening_id']})",
        f"**Unified Hiring Fit:** {report.get('unified_hiring_fit_score') if report.get('unified_hiring_fit_score') is not None else 'Incomplete'}%",
        f"**Final AI Recommendation:** {report['final_recommendation']['decision']} (Confidence: {conf_pct}%)",
        f"**Recruiter Decision:** {report['final_recommendation']['recruiter_decision']}",
        "",
        "---",
        "",
        "## 1. Executive Summary & Recommendation",
        f"- **Recommendation:** {report['final_recommendation']['decision']}",
        f"- **Confidence:** {conf_pct}% ({report['final_recommendation']['confidence_interpretation']})",
        f"- **Recruiter Review Status:** {report['final_recommendation']['recruiter_decision']}",
        "",
        "### Recommendation Rationale:",
    ]
    for reason in report["final_recommendation"]["reasons"]:
        lines.append(f"- {reason}")

    lines.extend(["", "## 2. Strengths"])
    for s in report["strengths"] or ["No distinct strengths recorded."]:
        lines.append(f"- {s}")

    lines.extend(["", "## 3. Weaknesses & Skill Gaps"])
    for w in report["weaknesses_and_skill_gaps"] or ["No substantial skill gaps recorded."]:
        lines.append(f"- {w}")

    ev = report["evaluation_summary"]
    lines.extend([
        "",
        "## 4. Round-by-Round Evaluation Breakdown",
        f"- **ATS Resume Score:** {ev['ats']['score'] if ev['ats']['score'] is not None else 'MISSING'} ({ev['ats']['status']})",
        f"- **HR Screening Score:** {ev['screening']['score'] if ev['screening']['score'] is not None else 'MISSING'} ({ev['screening']['status']})",
        f"- **HR Interview Score:** {ev['hr_interview']['score'] if ev['hr_interview']['score'] is not None else 'MISSING'} ({ev['hr_interview']['status']})",
        f"- **Technical Interview Score:** {ev['technical_interview']['score'] if ev['technical_interview']['score'] is not None else 'MISSING'} ({ev['technical_interview']['status']})",
        f"- **Machine Test Score:** {ev['machine_test']['score'] if ev['machine_test']['score'] is not None else 'MISSING'} ({ev['machine_test']['status']})",
        "",
        "## 5. Missing Data & Integrity / Behavioral Advisory",
        f"- **Missing Evaluation Rounds:** {', '.join(report['missing_evaluation_evidence']) or 'None'}",
        f"- **Integrity Risk Level:** {ev['integrity']['risk_level']} (Human Review Required: {ev['integrity']['human_review_required']})",
        f"- **Behavioral Consistency Index:** {ev['behavioral']['consistency_index'] if ev['behavioral']['consistency_index'] is not None else 'NOT_RECORDED'}",
        "",
        "## 6. Risk Indicators & Human Review Items",
    ])
    if report["risk_indicators"]:
        for r in report["risk_indicators"]:
            lines.append(f"- **{r['type'].upper()}**: {r['details']}")
    else:
        lines.append("- No critical risk factors identified.")

    lines.extend(["", "---", f"*{report['disclaimer']}*"])
    return "\n".join(lines)


def render_report_html(report: dict[str, Any]) -> str:
    """Renders structured report payload to polished, export-ready HTML format."""
    fit_score = report.get("unified_hiring_fit_score")
    fit_str = f"{fit_score:.1f}%" if fit_score is not None else "Pending / Incomplete"
    decision = report["final_recommendation"]["decision"]
    decision_color = "#10b981" if decision == "SELECTED" else ("#f59e0b" if decision == "HOLD_REVIEW" else "#ef4444")
    conf_pct = _format_confidence_pct(report["final_recommendation"].get("confidence"))

    ev = report["evaluation_summary"]
    weights = report.get("effective_weights") or {}

    def _round_row(label: str, key: str, data: dict[str, Any]) -> str:
        sc = data.get("score")
        st = data.get("status", "MISSING")
        wt = weights.get(key)
        wt_str = f"{float(wt)*100:.1f}%" if wt is not None else "—"
        sc_str = f"{float(sc):.1f} / 100" if sc is not None else "MISSING / NOT AVAILABLE"
        st_color = "#065f46" if sc is not None else "#92400e"
        return (
            f"<tr><td><strong>{escape(label)}</strong></td>"
            f"<td style='color:{st_color};font-weight:600;'>{escape(str(st))}</td>"
            f"<td>{escape(sc_str)}</td>"
            f"<td>{escape(wt_str)}</td></tr>"
        )

    rows_html = "".join([
        _round_row("1. Resume ATS Evaluation", "ats", ev["ats"]),
        _round_row("2. HR Screening Evaluation", "screening", ev["screening"]),
        _round_row("3. HR Interview Summary", "hr_interview", ev["hr_interview"]),
        _round_row("4. Technical Interview", "technical_interview", ev["technical_interview"]),
        _round_row("5. Machine Test Performance", "machine_test", ev["machine_test"]),
    ])

    strengths_li = "".join(f"<li>{escape(str(s))}</li>" for s in report["strengths"]) or "<li>No distinct strengths recorded yet.</li>"
    weaknesses_li = "".join(f"<li>{escape(str(w))}</li>" for w in report["weaknesses_and_skill_gaps"]) or "<li>No critical gaps detected.</li>"
    risks_li = "".join(f"<li><strong>{escape(str(r['type']).upper())}</strong>: {escape(str(r['details']))}</li>" for r in report["risk_indicators"]) or "<li>Zero unresolved risk indicators.</li>"
    reasons_li = "".join(f"<li>{escape(str(r))}</li>" for r in report["final_recommendation"]["reasons"])

    elig = ev.get("eligibility") or {}
    elig_str = f"{elig.get('status', 'NOT_EVALUATED')} — {elig.get('decision_explanation', 'No eligibility evaluation stored.')}"
    missing_str = ", ".join(report.get("missing_evaluation_evidence") or []) or "None (All 5 stages available)"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>{escape(report['report_title'])} - {escape(report['candidate_name'])}</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.55; color: #1f2937; margin: 0; padding: 32px; background: #f3f6f9; }}
  .container {{ max-width: 920px; margin: 0 auto; background: #ffffff; padding: 36px; border-radius: 10px; box-shadow: 0 4px 12px rgba(0,0,0,0.06); border: 1px solid #d9e2ec; }}
  .header {{ border-bottom: 2px solid #d9e2ec; padding-bottom: 18px; margin-bottom: 24px; display:flex; justify-content:space-between; align-items:flex-start; gap:16px; }}
  .badge {{ display: inline-block; padding: 6px 14px; border-radius: 9999px; font-weight: 700; font-size: 0.9rem; color: #fff; background: {decision_color}; }}
  .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap: 14px; margin: 18px 0; }}
  .card {{ background: #f8fafc; padding: 14px; border-radius: 8px; border: 1px solid #e2e8f0; }}
  .card-title {{ font-size: 0.72rem; text-transform: uppercase; color: #64748b; font-weight: 700; margin-bottom: 4px; }}
  .card-value {{ font-size: 1.35rem; font-weight: 800; color: #0f172a; }}
  table {{ width: 100%; border-collapse: collapse; margin: 12px 0 20px; }}
  th, td {{ border-bottom: 1px solid #e2e8f0; padding: 10px 8px; text-align: left; font-size: 0.92rem; }}
  th {{ background: #f1f5f9; color: #334e68; font-weight: 700; }}
  h1 {{ margin: 0; font-size: 1.55rem; color: #102a43; }}
  h2 {{ font-size: 1.15rem; border-bottom: 1px solid #e2e8f0; padding-bottom: 6px; margin-top: 24px; color: #102a43; }}
  ul {{ padding-left: 20px; margin: 8px 0; }}
  li {{ margin-bottom: 5px; }}
  .notice {{ background: #fff7df; border-left: 4px solid #d99000; padding: 12px 14px; font-size: 0.88rem; margin-top: 18px; }}
  .footer {{ margin-top: 28px; padding-top: 14px; border-top: 1px solid #e2e8f0; font-size: 0.8rem; color: #64748b; }}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <div>
      <h1>{escape(report['report_title'])}</h1>
      <p style="margin:4px 0 0; color:#52677b;">Target Role: <strong>{escape(str(report['target_role']))}</strong> | Opening: <strong>{escape(str(report['job_title']))}</strong></p>
      <p style="margin:4px 0 0; font-size:0.82rem; color:#64748b;">Report ID: {escape(str(report.get('report_id', 'N/A')))} | Version: v{escape(str(report.get('version', 1)))} | Generated: {escape(str(report.get('created_at', report.get('generated_at', ''))))}</p>
    </div>
    <div><span class="badge">{escape(decision)}</span></div>
  </div>

  <div class="grid">
    <div class="card">
      <div class="card-title">Candidate Overview</div>
      <div class="card-value" style="font-size:1.05rem;">{escape(report['candidate_name'])}</div>
      <small style="color:#64748b;">{escape(str(report['candidate_email'] or report['candidate_id']))}</small>
    </div>
    <div class="card">
      <div class="card-title">Cross-Round Fit</div>
      <div class="card-value">{escape(fit_str)}</div>
    </div>
    <div class="card">
      <div class="card-title">Evidence Confidence</div>
      <div class="card-value">{conf_pct}%</div>
    </div>
    <div class="card">
      <div class="card-title">Recruiter Approval</div>
      <div class="card-value" style="font-size:1.05rem;">{escape(str(report['final_recommendation']['recruiter_decision']))}</div>
    </div>
  </div>

  <h2>1. Multi-Round Evaluation Breakdown</h2>
  <table>
    <thead><tr><th>Assessment Stage</th><th>Status</th><th>Score</th><th>Normalized Weight</th></tr></thead>
    <tbody>{rows_html}</tbody>
  </table>
  <p style="font-size:0.88rem; color:#475569;"><strong>Missing / Unavailable Stages:</strong> {escape(missing_str)}</p>
  <p style="font-size:0.88rem; color:#475569;"><strong>Mandatory Eligibility Check:</strong> {escape(elig_str)}</p>

  <h2>2. AI Recommendation & Rationale</h2>
  <ul>{reasons_li}</ul>

  <h2>3. Candidate Strengths</h2>
  <ul style="color:#065f46;">{strengths_li}</ul>

  <h2>4. Weaknesses & Skill Gaps</h2>
  <ul style="color:#991b1b;">{weaknesses_li}</ul>

  <h2>5. Behavioral, Integrity & Risk Review</h2>
  <p style="font-size:0.9rem;"><strong>Integrity Risk Level:</strong> {escape(str(ev['integrity']['risk_level']))} | <strong>Human Review Required:</strong> {escape(str(ev['integrity']['human_review_required']))} | <strong>Behavioral Consistency Index:</strong> {escape(str(ev['behavioral']['consistency_index'] if ev['behavioral']['consistency_index'] is not None else 'Not Recorded'))}</p>
  <ul>{risks_li}</ul>

  <div class="notice">{escape(report['disclaimer'])}</div>
  <div class="footer">
    Recruiter Governance: {escape(str(report['recruiter_decision_workflow']['governance']))} | Confidentiality: Restricted Recruiter Access Only.
  </div>
</div>
</body>
</html>"""


def _pdf_escape(text: str) -> str:
    cleaned = text.replace("\u2014", "-").replace("\u2013", "-").replace("\u2022", "*")
    ascii_text = cleaned.encode("latin-1", "replace").decode("latin-1")
    return ascii_text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def render_report_pdf(report: dict[str, Any]) -> bytes:
    """
    Deterministic pure-Python PDF 1.4 generator for Hiring Intelligence Reports.
    Produces clean multi-page A4 PDF documents matching the exact backend report data
    with consistent headings, wrapped lines, page numbers, and confidentiality notice.
    """
    fit_score = report.get("unified_hiring_fit_score")
    fit_str = f"{fit_score:.1f}%" if fit_score is not None else "Pending / Incomplete"
    conf_pct = _format_confidence_pct(report["final_recommendation"].get("confidence"))
    ev = report["evaluation_summary"]
    weights = report.get("effective_weights") or {}

    raw_lines: list[tuple[str, int]] = [
        (report.get("report_title", "ZecPath Hiring Intelligence Report"), 15),
        (f"Report ID: {report.get('report_id', 'N/A')} | Version: v{report.get('version', 1)} | Generated: {report.get('created_at', report.get('generated_at', ''))}", 9),
        ("-" * 92, 9),
        (f"Candidate: {report['candidate_name']} ({report['candidate_id']}) | Email: {report.get('candidate_email', 'N/A')}", 10),
        (f"Target Role: {report['target_role']} | Job Opening: {report['job_title']} ({report.get('opening_id', 'N/A')})", 10),
        (f"Cross-Round Hiring Fit: {fit_str} | AI Recommendation: {report['final_recommendation']['decision']} | Confidence: {conf_pct}%", 10),
        (f"Recruiter Decision Status: {report['final_recommendation']['recruiter_decision']}", 10),
        ("", 8),
        ("1. ROUND-BY-ROUND EVALUATION BREAKDOWN", 12),
    ]

    for label, key in [
        ("ATS Resume", "ats"),
        ("HR Screening", "screening"),
        ("HR Interview", "hr_interview"),
        ("Technical Interview", "technical_interview"),
        ("Machine Test", "machine_test"),
    ]:
        data = ev.get(key, {})
        sc = data.get("score")
        st = data.get("status", "MISSING")
        wt = weights.get(key)
        wt_str = f"{float(wt)*100:.1f}%" if wt is not None else "N/A"
        sc_str = f"{float(sc):.1f}/100" if sc is not None else "MISSING"
        raw_lines.append((f"  - {label:22s} | Status: {st:12s} | Score: {sc_str:10s} | Weight: {wt_str}", 9))

    missing_str = ", ".join(report.get("missing_evaluation_evidence") or []) or "None"
    raw_lines.append((f"  Missing / Unavailable Stages: {missing_str}", 9))

    raw_lines.append(("", 8))
    raw_lines.append(("2. RECOMMENDATION RATIONALE", 12))
    for r in report["final_recommendation"].get("reasons", []) or ["No rationale recorded."]:
        raw_lines.append((f"  * {r}", 9))

    raw_lines.append(("", 8))
    raw_lines.append(("3. STRENGTHS", 12))
    for s in report.get("strengths", []) or ["No distinct strengths recorded."]:
        raw_lines.append((f"  + {s}", 9))

    raw_lines.append(("", 8))
    raw_lines.append(("4. WEAKNESSES & SKILL GAPS", 12))
    for w in report.get("weaknesses_and_skill_gaps", []) or ["No critical gaps detected."]:
        raw_lines.append((f"  - {w}", 9))

    raw_lines.append(("", 8))
    raw_lines.append(("5. INTEGRITY, BEHAVIORAL & RISK INDICATORS", 12))
    raw_lines.append((f"  Integrity Risk: {ev['integrity']['risk_level']} | Human Review Required: {ev['integrity']['human_review_required']}", 9))
    for r in report.get("risk_indicators", []) or [{"type": "none", "details": "No unresolved risk indicators."}]:
        raw_lines.append((f"  ! [{str(r['type']).upper()}] {r['details']}", 9))

    raw_lines.append(("", 8))
    raw_lines.append(("CONFIDENTIALITY & ADVISORY NOTICE", 11))
    raw_lines.append((report.get("disclaimer", ADVISORY_DISCLAIMER), 8))

    # Wrap long lines cleanly to 92 chars
    wrapped: list[tuple[str, int]] = []
    for text, size in raw_lines:
        if not text:
            wrapped.append(("", size))
            continue
        limit = 88 if size <= 10 else 72
        while len(text) > limit:
            cut = text.rfind(" ", 0, limit)
            if cut <= 0:
                cut = limit
            wrapped.append((text[:cut], size))
            text = "  " + text[cut:].lstrip()
        wrapped.append((text, size))

    # Paginate A4 (595 x 842 pts), top margin 790, bottom margin 55
    pages: list[list[tuple[str, int, int]]] = []
    current_page: list[tuple[str, int, int]] = []
    y = 790
    for text, size in wrapped:
        step = size + 6
        if y - step < 55:
            pages.append(current_page)
            current_page = []
            y = 790
        current_page.append((text, size, y))
        y -= step
    if current_page:
        pages.append(current_page)

    objects: list[bytes] = []
    # Obj 1: Catalog, Obj 2: Pages, Obj 3: Font Helvetica, Obj 4: Font Helvetica-Bold
    page_obj_nums: list[int] = []
    next_obj = 5
    page_entries: list[tuple[int, int, bytes]] = []
    total_pages = len(pages)

    for idx, p_lines in enumerate(pages, start=1):
        stream_cmds = ["BT"]
        for text, size, py in p_lines:
            font_name = "/F2" if size >= 11 else "/F1"
            stream_cmds.append(f"{font_name} {size} Tf 48 {py} Td ({_pdf_escape(text)}) Tj")
            stream_cmds.append(f"-48 -{py} Td")
        footer_text = f"ZecPath AI Hiring System - Confidential | Page {idx} of {total_pages}"
        stream_cmds.append(f"/F1 8 Tf 48 32 Td ({_pdf_escape(footer_text)}) Tj")
        stream_cmds.append("ET")
        stream_bytes = "\n".join(stream_cmds).encode("latin-1", "replace")

        page_num = next_obj
        content_num = next_obj + 1
        next_obj += 2
        page_obj_nums.append(page_num)
        page_entries.append((page_num, content_num, stream_bytes))

    kids_str = " ".join(f"{n} 0 R" for n in page_obj_nums)
    objects.append(b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n")
    objects.append(f"2 0 obj\n<< /Type /Pages /Kids [{kids_str}] /Count {len(page_obj_nums)} >>\nendobj\n".encode("ascii"))
    objects.append(b"3 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n")
    objects.append(b"4 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>\nendobj\n")

    for page_num, content_num, stream_bytes in page_entries:
        page_dict = (
            f"{page_num} 0 obj\n"
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
            f"/Resources << /Font << /F1 3 0 R /F2 4 0 R >> >> "
            f"/Contents {content_num} 0 R >>\nendobj\n"
        ).encode("ascii")
        content_dict = (
            f"{content_num} 0 obj\n<< /Length {len(stream_bytes)} >>\nstream\n".encode("ascii")
            + stream_bytes
            + b"\nendstream\nendobj\n"
        )
        objects.append(page_dict)
        objects.append(content_dict)

    pdf_parts = [b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n"]
    offsets = [0]
    current_len = len(pdf_parts[0])
    for obj in objects:
        offsets.append(current_len)
        pdf_parts.append(obj)
        current_len += len(obj)

    xref_pos = current_len
    xref_lines = [f"xref\n0 {len(offsets)}\n0000000000 65535 f \n".encode("ascii")]
    for off in offsets[1:]:
        xref_lines.append(f"{off:010d} 00000 n \n".encode("ascii"))
    trailer = (
        f"trailer\n<< /Size {len(offsets)} /Root 1 0 R >>\n"
        f"startxref\n{xref_pos}\n%%EOF\n"
    ).encode("ascii")
    return b"".join(pdf_parts + xref_lines + [trailer])
