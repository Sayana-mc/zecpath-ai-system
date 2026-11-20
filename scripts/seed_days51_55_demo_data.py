"""Idempotent synthetic demo data seeder for Days 51-55 (ZecPath AI Hiring System)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src import auth, database
from src.cross_round_scoring_engine import cross_round_scoring_engine
from src.final_recommendation_engine import get_decision_rules_for_role, recommend_candidate
from src.hiring_intelligence_report_generator import generate_candidate_hiring_report
from src.optimization_engine import optimization_engine
from src.security_governance import security_governance


def _upsert_opening(opening_id: str, title: str, description: str, requirements: list[str], tenant_id: str) -> None:
    now = database._now()
    with database._connection() as conn:
        existing = conn.execute("SELECT opening_id FROM openings WHERE opening_id = ?", (opening_id,)).fetchone()
        if existing:
            conn.execute(
                """
                UPDATE openings
                SET title = ?, description = ?, required_skills = ?, preferred_skills = ?,
                    status = 'OPEN', tenant_id = ?, updated_at = ?
                WHERE opening_id = ?
                """,
                (title, description, json.dumps(requirements), json.dumps([]), tenant_id, now, opening_id),
            )
        else:
            conn.execute(
                """
                INSERT INTO openings (
                    opening_id, title, description, required_skills, preferred_skills,
                    minimum_education, minimum_years_experience, status, tenant_id, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, 'Bachelor', 1.0, 'OPEN', ?, ?, ?)
                """,
                (opening_id, title, description, json.dumps(requirements), json.dumps([]), tenant_id, now, now),
            )


def _upsert_candidate(
    candidate_id: str,
    opening_id: str,
    name: str,
    email: str,
    skills: list[str],
    experience_years: int,
    education: str,
    ats_score: float,
    eligibility_status: str,
    eligibility_explanation: str,
    tenant_id: str = "default_tenant",
) -> None:
    now = database._now()
    resume_text = (
        f"Candidate: {name}\n"
        f"Experience: {experience_years} years\n"
        f"Education: {education}\n"
        f"Skills: {', '.join(skills)}\n"
        f"Summary: Synthetic demo profile for ZecPath AI Hiring System verification."
    )
    resume_data = json.dumps(
        {
            "skills": skills,
            "experience_years": experience_years,
            "education": education,
            "eligibility_status": eligibility_status,
            "eligibility_explanation": eligibility_explanation,
        }
    )
    score_evidence = json.dumps(
        {
            "ats_score": ats_score,
            "eligibility_status": eligibility_status,
            "eligibility_explanation": eligibility_explanation,
        }
    )
    with database._connection() as conn:
        existing = conn.execute("SELECT candidate_id FROM candidates WHERE candidate_id = ?", (candidate_id,)).fetchone()
        if existing:
            conn.execute(
                """
                UPDATE candidates
                SET opening_id = ?, name = ?, email = ?, skills = ?, resume_text = ?,
                    resume_data = ?, application_status = 'INTERVIEW', score = ?,
                    score_evidence = ?, tenant_id = ?, updated_at = ?
                WHERE candidate_id = ?
                """,
                (
                    opening_id, name, email, json.dumps(skills), resume_text,
                    resume_data, ats_score, score_evidence, tenant_id, now, candidate_id,
                ),
            )
        else:
            conn.execute(
                """
                INSERT INTO candidates (
                    candidate_id, name, email, opening_id, skills, resume_text,
                    resume_data, application_status, score, score_evidence,
                    tenant_id, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, 'INTERVIEW', ?, ?, ?, ?, ?)
                """,
                (
                    candidate_id, name, email, opening_id, json.dumps(skills), resume_text,
                    resume_data, ats_score, score_evidence, tenant_id, now, now,
                ),
            )
        elig_result = json.dumps(
            {
                "status": eligibility_status,
                "decision_explanation": eligibility_explanation,
                "rules": {},
                "review_reasons": [] if eligibility_status == "ELIGIBLE" else [eligibility_explanation],
                "missing_information": [],
            }
        )
        conn.execute(
            """
            INSERT OR REPLACE INTO eligibility_evaluations (
                evaluation_id, candidate_id, opening_id, configuration_version,
                input_fingerprint, result_json, evaluated_at
            ) VALUES (?, ?, ?, 1, ?, ?, ?)
            """,
            (f"elig_seed_{candidate_id}", candidate_id, opening_id, f"seed_{candidate_id}", elig_result, now),
        )


def _seed_stage_records(
    candidate_id: str,
    opening_id: str,
    target_role: str,
    screening_score: float | None,
    hr_score: float | None,
    tech_score: float | None,
    mt_score: float | None,
    mt_pending: bool = False,
    integrity_flagged: bool = False,
    behav_consistency: float = 88.0,
) -> None:
    now = database._now()
    with database._connection() as conn:
        # 1. Screening
        if screening_score is not None:
            sess_id = f"scr_sess_{candidate_id}"
            if not conn.execute("SELECT session_id FROM screening_sessions WHERE session_id = ?", (sess_id,)).fetchone():
                conn.execute(
                    """
                    INSERT INTO screening_sessions
                    (session_id, candidate_id, opening_id, status, language, started_at, completed_at, source, version, created_at, updated_at)
                    VALUES (?, ?, ?, 'COMPLETED', 'en', ?, ?, 'demo_seed', 1, ?, ?)
                    """,
                    (sess_id, candidate_id, opening_id, now, now, now, now),
                )
            agg_id = f"scr_agg_{candidate_id}"
            conn.execute(
                """
                INSERT OR REPLACE INTO screening_aggregate_scores
                (aggregate_id, session_id, candidate_id, overall_score, score_status,
                 questions_evaluated, questions_answered, questions_missing,
                 human_review_required, scoring_version, created_at, updated_at)
                VALUES (?, ?, ?, ?, 'FINAL', 5, 5, 0, 0, 'v1', ?, ?)
                """,
                (agg_id, sess_id, candidate_id, screening_score, now, now),
            )

        # 2. HR Interview
        if hr_score is not None:
            hr_id = f"hr_int_{candidate_id}"
            if not conn.execute("SELECT interview_id FROM hr_interview_sessions WHERE interview_id = ?", (hr_id,)).fetchone():
                conn.execute(
                    """
                    INSERT INTO hr_interview_sessions
                    (interview_id, candidate_id, opening_id, status, current_phase, experience_level, role_type, recruiter_id, created_at, updated_at)
                    VALUES (?, ?, ?, 'COMPLETED', 'COMPLETED', 'EXPERIENCED', 'TECHNICAL', 'recruiter-d41-52', ?, ?)
                    """,
                    (hr_id, candidate_id, opening_id, now, now),
                )
            conn.execute(
                """
                INSERT OR REPLACE INTO hr_interview_scores
                (score_id, interview_id, candidate_id, relevance_score, communication_score,
                 confidence_score, consistency_score, overall_hr_score, score_status,
                 breakdown, human_review_required, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'FINAL', ?, 0, ?, ?)
                """,
                (
                    f"hr_sc_{candidate_id}", hr_id, candidate_id, hr_score, hr_score - 1.5,
                    hr_score + 1.0, hr_score, hr_score,
                    json.dumps({"summary": f"HR communication and alignment evaluated at {hr_score:.1f}%."}),
                    now, now,
                ),
            )

        # 3. Technical Interview
        if tech_score is not None:
            tech_id = f"tech_sess_{candidate_id}"
            conn.execute(
                """
                INSERT OR REPLACE INTO technical_interview_sessions
                (session_id, candidate_id, opening_id, target_role, experience_level, status, current_stage, total_questions, overall_score, rubric_breakdown, created_at, updated_at)
                VALUES (?, ?, ?, ?, 'mid_senior', 'COMPLETED', 'COMPLETED', 5, ?, ?, ?, ?)
                """,
                (tech_id, candidate_id, opening_id, target_role, tech_score, json.dumps({"core_concepts": tech_score}), now, now),
            )

        # 4. Machine Test
        if mt_score is not None or mt_pending:
            assign_id = f"mt_assign_{candidate_id}"
            conn.execute(
                """
                INSERT OR REPLACE INTO machine_test_assignments
                (assignment_id, candidate_id, opening_id, task_type, task_id, title, description, time_limit_minutes, status, assigned_at, completed_at)
                VALUES (?, ?, ?, 'coding', 'task_pipeline_01', ?, ?, 60, ?, ?, ?)
                """,
                (
                    assign_id, candidate_id, opening_id,
                    f"{target_role} Practical Coding Test",
                    "Implement a reliable data processing pipeline with unit tests and error handling.",
                    "ASSIGNED" if mt_pending else "EVALUATED",
                    now, None if mt_pending else now,
                ),
            )
            if mt_score is not None and not mt_pending:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO machine_test_submissions
                    (submission_id, assignment_id, code_content, language, time_spent_minutes, total_score, rubric_scores, execution_details, status, submitted_at)
                    VALUES (?, ?, ?, 'python', 38.5, ?, ?, ?, 'EVALUATED', ?)
                    """,
                    (
                        f"mt_sub_{candidate_id}", assign_id,
                        "def solve(items):\n    return [x for x in items if x is not None]\n",
                        mt_score,
                        json.dumps({"correctness": mt_score, "code_quality": mt_score - 2.0}),
                        json.dumps({"passed_cases": int(round(mt_score / 10)), "total_cases": 10}),
                        now,
                    ),
                )

    # 5. Integrity & Behavioral
    existing_int = database.get_candidate_integrity_records(candidate_id)
    if not existing_int:
        database.save_candidate_integrity_record(
            candidate_id=candidate_id,
            session_id=f"sess_{candidate_id}",
            round_type="machine_test",
            has_consent=True,
            total_risk_points=15 if integrity_flagged else 0,
            risk_level="HIGH" if integrity_flagged else "LOW",
            requires_human_review=integrity_flagged,
            events=[{"event": "tab_switch", "count": 3}] if integrity_flagged else [],
            review_flags=[{"flag": "Multiple tab switches detected"}] if integrity_flagged else [],
        )

    existing_beh = database.get_candidate_behavioral_records(candidate_id)
    if not existing_beh:
        database.save_candidate_behavioral_record(
            candidate_id=candidate_id,
            session_id=f"sess_{candidate_id}",
            round_type="hr_interview",
            has_consent=True,
            consistency_index=behav_consistency,
            requires_human_review=behav_consistency < 65,
            observations=[
                {
                    "signal": "structured_reasoning",
                    "impact": "positive" if behav_consistency >= 70 else "negative",
                    "note": "Clear architectural reasoning" if behav_consistency >= 70 else "Brief hesitation on follow-up probes",
                }
            ],
            disclaimer="Behavioral operational indicators only; no emotion detection.",
        )

    # 6. Consents (Day 55) - reset baseline consents for clean idempotent seeding
    with database._connection() as conn:
        conn.execute("DELETE FROM candidate_consents WHERE candidate_id = ?", (candidate_id,))
    database.record_candidate_consent(
        candidate_id=candidate_id,
        purpose="ai_assessment",
        granted=True,
        actor_id="recruiter-d41-52",
        consent_version="consent-v2",
        notes="Verified candidate consent during onboarding",
    )
    database.record_candidate_consent(
        candidate_id=candidate_id,
        purpose="integrity_monitoring",
        granted=True,
        actor_id="recruiter-d41-52",
        consent_version="consent-v2",
        notes="Verified integrity monitoring consent",
    )


def seed_all() -> dict[str, int]:
    database.initialize_database()
    with database._connection() as conn:
        conn.execute("DELETE FROM recruiter_login_attempts")

    # 1. Seed 3 recruiter accounts for RBAC & Tenant tests
    accounts = [
        ("recruiter-d41-52", "Password123!LongEnough", "admin", "default_tenant"),
        ("junior_recruiter", "JuniorDemo123!", "recruiter", "default_tenant"),
        ("tenant_b_recruiter", "TenantBDemo123!", "admin", "tenant_b"),
    ]
    for username, pwd, role, tenant_id in accounts:
        salt, pw_hash = auth.hash_recruiter_password(pwd)
        database.upsert_recruiter_account(
            username=username,
            password_salt=salt,
            password_hash=pw_hash,
            role=role,
            tenant_id=tenant_id,
        )

    # 2. Seed Job Openings
    _upsert_opening(
        "open_python_dev",
        "Python Developer",
        "Build FastAPI backend services, SQLite/PostgreSQL data pipelines, and automated test suites.",
        ["Python", "FastAPI", "SQL", "Pytest", "REST APIs"],
        "default_tenant",
    )
    _upsert_opening(
        "open_data_analyst",
        "Data Analyst",
        "Analyze hiring funnels, build KPI dashboards, and validate SQL/Python analytical models.",
        ["SQL", "Python", "Pandas", "Statistics", "Data Visualization"],
        "default_tenant",
    )
    _upsert_opening(
        "open_mern_dev",
        "MERN Stack Developer",
        "Develop full-stack MongoDB, Express, React, and Node.js web applications.",
        ["React", "Node.js", "Express", "MongoDB", "JavaScript"],
        "default_tenant",
    )
    _upsert_opening(
        "open_tenant_b_qa",
        "QA Automation Engineer",
        "Tenant B isolated job opening for cross-tenant security verification.",
        ["Playwright", "Python", "CI/CD"],
        "tenant_b",
    )

    # 3. Seed 5 realistic default_tenant candidates + 1 tenant_b candidate
    profiles = [
        {
            "candidate_id": "cand_arun_kumar",
            "opening_id": "open_python_dev",
            "role_key": "python_developer",
            "target_role": "Python Developer",
            "name": "Arun Kumar",
            "email": "arun.kumar.demo@zecpath.example",
            "skills": ["Python", "FastAPI", "SQL", "Docker", "Pytest"],
            "experience_years": 4,
            "education": "B.Tech Computer Science",
            "ats": 91.0,
            "screening": 88.0,
            "hr": 86.0,
            "tech": 90.0,
            "mt": 92.0,
            "mt_pending": False,
            "eligibility_status": "ELIGIBLE",
            "eligibility_explanation": "Meets all mandatory Python, FastAPI, and 4 years experience criteria.",
            "integrity_flagged": False,
            "behav_consistency": 92.0,
        },
        {
            "candidate_id": "cand_neha_thomas",
            "opening_id": "open_data_analyst",
            "role_key": "data_analyst",
            "target_role": "Data Analyst",
            "name": "Neha Thomas",
            "email": "neha.thomas.demo@zecpath.example",
            "skills": ["SQL", "Python", "Pandas", "Power BI", "Statistics"],
            "experience_years": 3,
            "education": "M.Sc Data Science",
            "ats": 88.0,
            "screening": 86.0,
            "hr": 85.0,
            "tech": 87.0,
            "mt": 89.0,
            "mt_pending": False,
            "eligibility_status": "ELIGIBLE",
            "eligibility_explanation": "Meets all mandatory SQL, Python, and analytical modeling criteria.",
            "integrity_flagged": False,
            "behav_consistency": 90.0,
        },
        {
            "candidate_id": "cand_rahul_menon",
            "opening_id": "open_mern_dev",
            "role_key": "mern_developer",
            "target_role": "MERN Stack Developer",
            "name": "Rahul Menon",
            "email": "rahul.menon.demo@zecpath.example",
            "skills": ["React", "Node.js", "JavaScript", "MongoDB"],
            "experience_years": 2,
            "education": "B.E. Information Technology",
            "ats": 70.0,
            "screening": 68.0,
            "hr": 66.0,
            "tech": 64.0,
            "mt": 65.0,
            "mt_pending": False,
            "eligibility_status": "ELIGIBLE",
            "eligibility_explanation": "Borderline technical depth; eligible for human review.",
            "integrity_flagged": False,
            "behav_consistency": 74.0,
        },
        {
            "candidate_id": "cand_vivek_raj",
            "opening_id": "open_python_dev",
            "role_key": "python_developer",
            "target_role": "Python Developer",
            "name": "Vivek Raj",
            "email": "vivek.raj.demo@zecpath.example",
            "skills": ["Python", "Django", "SQL"],
            "experience_years": 3,
            "education": "B.Tech Software Engineering",
            "ats": 83.0,
            "screening": 81.0,
            "hr": 79.0,
            "tech": 82.0,
            "mt": None,
            "mt_pending": True,
            "eligibility_status": "ELIGIBLE",
            "eligibility_explanation": "Machine Test assigned and pending submission.",
            "integrity_flagged": False,
            "behav_consistency": 84.0,
        },
        {
            "candidate_id": "cand_anjali_nair",
            "opening_id": "open_data_analyst",
            "role_key": "data_analyst",
            "target_role": "Data Analyst",
            "name": "Anjali Nair",
            "email": "anjali.nair.demo@zecpath.example",
            "skills": ["Excel", "Tableau", "Python"],
            "experience_years": 1,
            "education": "B.Sc Mathematics",
            "ats": 84.0,
            "screening": 82.0,
            "hr": 80.0,
            "tech": 83.0,
            "mt": 81.0,
            "mt_pending": False,
            "eligibility_status": "REJECTED",
            "eligibility_explanation": "Mandatory qualification check failed: minimum 2 years SQL production experience required.",
            "integrity_flagged": False,
            "behav_consistency": 86.0,
        },
    ]

    for p in profiles:
        _upsert_candidate(
            candidate_id=p["candidate_id"],
            opening_id=p["opening_id"],
            name=p["name"],
            email=p["email"],
            skills=p["skills"],
            experience_years=p["experience_years"],
            education=p["education"],
            ats_score=p["ats"],
            eligibility_status=p["eligibility_status"],
            eligibility_explanation=p["eligibility_explanation"],
            tenant_id="default_tenant",
        )
        _seed_stage_records(
            candidate_id=p["candidate_id"],
            opening_id=p["opening_id"],
            target_role=p["target_role"],
            screening_score=p["screening"],
            hr_score=p["hr"],
            tech_score=p["tech"],
            mt_score=p["mt"],
            mt_pending=p["mt_pending"],
            integrity_flagged=p["integrity_flagged"],
            behav_consistency=p["behav_consistency"],
        )

        # Clear stale pre-existing Day 51-53 records for this demo candidate so seeded 5-stage state is latest
        with database._connection() as conn:
            conn.execute("DELETE FROM hiring_intelligence_reports WHERE candidate_id = ?", (p["candidate_id"],))
            conn.execute("DELETE FROM final_recommendations WHERE candidate_id = ?", (p["candidate_id"],))
            conn.execute("DELETE FROM cross_round_evaluations WHERE candidate_id = ?", (p["candidate_id"],))

        # Day 51 Cross-Round Evaluation (idempotent via fingerprint)
        stage_data = cross_round_scoring_engine.collect_candidate_stage_data(p["candidate_id"])
        cross_eval = cross_round_scoring_engine.calculate_hiring_fit(
            candidate_id=p["candidate_id"],
            target_role=p["role_key"],
            round_scores=stage_data["stage_scores"],
            opening_id=p["opening_id"],
            stage_status=stage_data["stage_status"],
            min_required_stages=3,
            recalculation_reason="Seeded initial 5-stage cross-round evaluation",
            save_to_db=True,
        )

        # Day 52 Final Recommendation (only if none exists yet)
        if not database.list_final_recommendations(candidate_id=p["candidate_id"]):
            rules = get_decision_rules_for_role(p["role_key"])
            completed_cnt = cross_eval.get("completed_rounds", 0)
            rec_res = recommend_candidate(
                {
                    "candidate_id": p["candidate_id"],
                    "session_id": f"sess_{p['candidate_id']}",
                    "target_role": p["target_role"],
                    "assessment_status": "COMPLETE" if completed_cnt >= 5 else "INCOMPLETE",
                    "unified_score": cross_eval.get("hiring_fit_percentage") or p["ats"],
                    "completed_rounds": completed_cnt,
                    "expected_rounds": 5,
                    "evidence_quality": 92.0 if completed_cnt >= 5 else 72.0,
                    "data_consistency": 90.0,
                    "eligibility_status": p["eligibility_status"],
                    "eligibility_reason": p["eligibility_explanation"],
                    "stage_status": stage_data["stage_status"],
                    "rounds": stage_data["stage_scores"],
                    "risk_factors": {
                        "integrity": {"flag": p["integrity_flagged"], "evidence": [], "source": "Integrity Subsystem"},
                        "behavior": {"flag": False, "evidence": [], "source": "Behavioral Subsystem"},
                    },
                },
                rules=rules,
            )
            exp = rec_res.get("explanation", {})
            cm = rec_res.get("confidence_methodology")
            cm_str = cm.get("formula", json.dumps(cm)) if isinstance(cm, dict) else str(cm or "")
            saved_rec = database.save_final_recommendation(
                candidate_id=p["candidate_id"],
                opening_id=p["opening_id"],
                target_role=p["target_role"],
                decision=rec_res["decision"],
                score=rec_res["score"],
                confidence=rec_res["confidence"],
                completed_rounds=completed_cnt,
                expected_rounds=5,
                reasons=exp.get("reasons", []),
                risk_factors=rec_res["risk_factors"],
                reason_codes=rec_res.get("reason_codes", exp.get("reason_codes", [])),
                strengths=rec_res.get("strengths", []),
                weaknesses=rec_res.get("weaknesses", []),
                missing_evidence=rec_res.get("missing_evidence", []),
                threshold_config=rules,
                confidence_methodology=cm_str,
                eligibility_status=p["eligibility_status"],
            )
            if p["candidate_id"] == "cand_arun_kumar":
                database.update_final_recommendation_decision(
                    recommendation_id=saved_rec["recommendation_id"],
                    recruiter_decision="APPROVED",
                    recruiter_notes="Strong Python/FastAPI performance across all 5 rounds.",
                    actor_id="recruiter-d41-52",
                )

        # Day 53 Hiring Intelligence Report (only if none exists yet)
        if not database.get_latest_hiring_intelligence_report(p["candidate_id"]):
            rep = generate_candidate_hiring_report(
                candidate_id=p["candidate_id"],
                recruiter_id="recruiter-d41-52",
                save_to_db=True,
            )
            security_governance.log_audit_event(
                event_type="DEMO_REPORT_SEEDED",
                actor_id="recruiter-d41-52",
                subject_id=p["candidate_id"],
                details={"report_id": rep.get("report_id"), "version": rep.get("version", 1)},
            )

    # Tenant B isolated candidate
    _upsert_candidate(
        candidate_id="cand_tenant_b_qa",
        opening_id="open_tenant_b_qa",
        name="Tenant B Test Candidate",
        email="tenant.b.qa@zecpath.example",
        skills=["Playwright", "Python"],
        experience_years=3,
        education="B.Tech CS",
        ats_score=85.0,
        eligibility_status="ELIGIBLE",
        eligibility_explanation="Isolated tenant_b candidate.",
        tenant_id="tenant_b",
    )

    # Day 54 Initial Optimization Run
    if not database.list_optimization_runs(limit=1):
        optimization_engine.run_full_optimization_analysis(
            strong_threshold=80.0,
            potential_threshold=60.0,
            actor_id="recruiter-d41-52",
            tenant_id="default_tenant",
            save_to_db=True,
        )

    return {"candidates_seeded": len(profiles) + 1, "accounts_seeded": len(accounts)}


if __name__ == "__main__":
    summary = seed_all()
    print(json.dumps(summary, indent=2))
