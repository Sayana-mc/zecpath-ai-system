"""Day 56: Full System Simulation Pipeline & AI vs Human Comparison Engine."""

import time
from typing import Any
try:
    from . import database
except ImportError:
    from src import database
from .cross_round_scoring_engine import cross_round_scoring_engine
from .final_recommendation_engine import recommend_candidate
from .hiring_intelligence_report_generator import generate_candidate_hiring_report


class SystemSimulationPipeline:
    """Orchestrates end-to-end 15-stage hiring simulations and compares AI vs. human assessments."""

    @staticmethod
    def simulate_candidate_pipeline(
        candidate_data: dict[str, Any],
        opening_data: dict[str, Any],
        recruiter_id: str = "rec_admin_01",
    ) -> dict[str, Any]:
        """
        Executes complete 15-stage simulated lifecycle:
        Login -> Job -> Candidate -> Resume -> ATS -> Eligibility ->
        Screening -> HR Interview -> Tech Interview -> Machine Test ->
        Cross-Round Scoring -> Recommendation -> Report -> Decision -> Audit.
        """
        timings: dict[str, float] = {}
        statuses: dict[str, str] = {}

        def record_stage(name: str, fn):
            t0 = time.perf_counter()
            try:
                res = fn()
                statuses[name] = "COMPLETED"
                return res
            except Exception as e:
                statuses[name] = f"FAILED: {e}"
                raise
            finally:
                timings[name] = round((time.perf_counter() - t0) * 1000, 2)

        # 1-2. Job Setup
        opening = record_stage(
            "job_creation",
            lambda: database.save_opening(
                title=opening_data.get("title", "Full Stack Engineer"),
                description=opening_data.get("description", "FastAPI and React role"),
                requirements=opening_data.get("requirements", ["Python", "FastAPI", "PostgreSQL"]),
                preferred_skills=opening_data.get("preferred_skills", ["Docker", "Redis"]),
            ),
        )
        op_id = opening["opening_id"]

        # 3. Candidate Registration
        candidate = record_stage(
            "candidate_registration",
            lambda: database.create_candidate(
                name=candidate_data.get("name", "Simulated Candidate"),
                email=candidate_data.get("email", f"sim_{int(time.time())}@example.com"),
                opening_id=op_id,
                skills=candidate_data.get("skills", ["Python", "FastAPI", "SQL"]),
            ),
        )
        cand_id = candidate["candidate_id"]

        # 4-5. Resume Attachment & Extraction
        resume_text = candidate_data.get(
            "resume_text",
            "Experienced software engineer with 5 years in Python, FastAPI, PostgreSQL, and AWS microservices."
        )
        record_stage(
            "resume_processing",
            lambda: database.save_candidate_resume(
                candidate_id=cand_id,
                filename="simulated_resume.txt",
                parsed_text=resume_text,
                resume_data={"skills": ["Python", "FastAPI", "PostgreSQL", "AWS"]},
            ),
        )

        # 6. ATS Scoring
        ats_score = candidate_data.get("ats_score", 85.0)
        record_stage(
            "ats_scoring",
            lambda: database.save_candidate_score(
                candidate_id=cand_id,
                score=ats_score,
                evidence={"matched_required_skills": ["Python", "FastAPI"], "missing_required_skills": []},
            ),
        )

        # 7. Eligibility Evaluation
        eligibility_result = record_stage(
            "eligibility_evaluation",
            lambda: database.save_candidate_eligibility_evaluation(
                candidate_id=cand_id,
                opening_id=op_id,
                eligibility_status="ELIGIBLE",
                failed_thresholds=[],
                missing_information=[],
                details={"verified_skills": ["Python", "FastAPI"]},
            ),
        )

        # 8. HR Screening
        screening_score = candidate_data.get("screening_score", 82.0)
        record_stage(
            "hr_screening",
            lambda: database.save_screening_session_full(
                candidate_id=cand_id,
                opening_id=op_id,
                overall_score=screening_score,
                status="COMPLETED",
                summary_notes="Candidate demonstrated structured articulation and cultural fit.",
            ),
        )

        # 9. HR Interview
        hr_score = candidate_data.get("hr_interview_score", 80.0)
        record_stage(
            "hr_interview",
            lambda: database.create_hr_interview(
                candidate_id=cand_id,
                opening_id=op_id,
                candidate_experience_level="mid",
                overall_score=hr_score,
                status="COMPLETED",
            ),
        )

        # 10. Technical Interview
        tech_score = candidate_data.get("technical_interview_score", 88.0)
        tech_session = record_stage(
            "technical_interview",
            lambda: database.create_technical_interview_session(
                candidate_id=cand_id,
                opening_id=op_id,
                target_role=opening["title"],
                experience_level="mid",
            ),
        )
        database.save_technical_interview_response({
            "response_id": f"sim_resp_{cand_id[:6]}",
            "interview_id": tech_session["session_id"],
            "question_id": "sim_q1",
            "answer_text": "Production system design with PostgreSQL connection pooling and async celery workers.",
            "accuracy_score": 4.5,
            "depth_score": 4.5,
            "reasoning_score": 4.2,
            "applicability_score": 4.0,
            "depth_classification": "deep",
            "weighted_score": tech_score,
            "normalized_score": tech_score,
            "explanation": "High depth architectural solution.",
        })
        database.update_technical_interview_session_status(tech_session["session_id"], "COMPLETED")

        # 11. Machine Test
        machine_score = candidate_data.get("machine_test_score", 86.0)
        m_test = record_stage(
            "machine_test",
            lambda: database.create_machine_test_assignment(
                candidate_id=cand_id,
                opening_id=op_id,
                task_type="coding",
                task_id="task_coding_01",
                title="Async Worker Task",
                description="Implement resilient queue worker.",
                time_limit_minutes=45,
            ),
        )
        database.save_machine_test_submission({
            "submission_id": f"sub_sim_{cand_id[:6]}",
            "test_id": m_test.get("test_id") or m_test.get("assignment_id"),
            "candidate_id": cand_id,
            "code_content": "async def worker(): pass",
            "elapsed_time_minutes": 22.0,
            "correctness_score": 90.0,
            "efficiency_score": 85.0,
            "code_quality_score": 88.0,
            "problem_solving_score": 85.0,
            "time_management_score": 90.0,
            "total_score": machine_score,
            "test_results": [{"passed": True}],
            "evaluation_summary": "Passed all unit tests.",
        })
        database.update_machine_test_assignment_status(m_test["test_id"], "EVALUATED")

        # 12. Cross-Round Scoring
        round_scores = {
            "ats": ats_score,
            "screening": screening_score,
            "hr_interview": hr_score,
            "technical_interview": tech_score,
            "machine_test": machine_score,
        }
        cross_eval = record_stage(
            "cross_round_scoring",
            lambda: cross_round_scoring_engine.calculate_unified_fit(
                round_scores=round_scores,
                target_role="software_engineer",
                candidate_id=cand_id,
            ),
        )
        database.save_cross_round_evaluation({
            "candidate_id": cand_id,
            "opening_id": op_id,
            "target_role": opening["title"],
            "hiring_fit_percentage": cross_eval["hiring_fit_percentage"],
            "round_scores": round_scores,
            "effective_weights": cross_eval["effective_weights"],
            "completed_rounds": cross_eval["completed_rounds_count"],
            "missing_rounds": cross_eval["missing_rounds"],
            "anomalies": cross_eval["anomalies"],
        })

        # 13. Final Recommendation
        rec_input = {
            "candidate_id": cand_id,
            "session_id": f"sim_sess_{cand_id[:6]}",
            "target_role": opening["title"],
            "assessment_status": "COMPLETE",
            "unified_score": cross_eval["hiring_fit_percentage"],
            "completed_rounds": 5,
            "expected_rounds": 5,
            "evidence_quality": 95.0,
            "data_consistency": 90.0,
            "rounds": round_scores,
            "risk_factors": {"integrity": {"flag": False}, "behavior": {"flag": False}},
        }
        final_rec = record_stage(
            "final_recommendation",
            lambda: recommend_candidate(rec_input),
        )
        database.save_final_recommendation(
            candidate_id=cand_id,
            opening_id=op_id,
            target_role=opening["title"],
            decision=final_rec["decision"],
            score=final_rec["score"],
            confidence=final_rec["confidence"],
            completed_rounds=5,
            expected_rounds=5,
            reasons=final_rec["explanation"]["reasons"],
            risk_factors=final_rec["risk_factors"],
        )

        # 14. Hiring Intelligence Report Generation
        report = record_stage(
            "hiring_report_generation",
            lambda: generate_candidate_hiring_report(cand_id, recruiter_id=recruiter_id),
        )

        # 15. Recruiter Decision Approval
        record_stage(
            "recruiter_decision",
            lambda: database.update_final_recommendation_decision(
                recommendation_id=report["final_recommendation"]["reasons"] and database.list_final_recommendations(cand_id)[0]["recommendation_id"],
                recruiter_decision="APPROVED",
                recruiter_notes="Simulated hiring decision approved following human recruiter review.",
            ),
        )

        total_duration = round(sum(timings.values()), 2)

        return {
            "candidate_id": cand_id,
            "opening_id": op_id,
            "unified_fit_score": cross_eval["hiring_fit_percentage"],
            "ai_recommendation": final_rec["decision"],
            "report_id": report.get("report_id"),
            "stage_statuses": statuses,
            "stage_timings_ms": timings,
            "total_execution_ms": total_duration,
            "pipeline_success": all(s == "COMPLETED" for s in statuses.values()),
        }

    @staticmethod
    def compare_ai_vs_human_evaluations(
        simulation_results: list[dict[str, Any]],
        human_evaluations: list[dict[str, Any]],
    ) -> dict[str, Any]:
        """
        Compares AI-generated final scores and decisions against independent human review rubrics.
        Calculates score gaps, decision alignment rate, and logs discrepancies.
        """
        comparisons = []
        gaps = []
        decision_matches = 0

        for sim, human in zip(simulation_results, human_evaluations):
            ai_score = float(sim.get("unified_fit_score", 0.0))
            ai_decision = str(sim.get("ai_recommendation", "HOLD_REVIEW"))
            human_score = float(human.get("human_score", 0.0))
            human_decision = str(human.get("human_decision", "HOLD_REVIEW"))

            gap = round(abs(ai_score - human_score), 2)
            gaps.append(gap)
            aligned = (ai_decision == human_decision)
            if aligned:
                decision_matches += 1

            discrepancy_note = None
            if not aligned:
                discrepancy_note = (
                    f"AI recommended {ai_decision} (Score {ai_score}) whereas human reviewer "
                    f"concluded {human_decision} (Score {human_score})."
                )

            comparisons.append({
                "candidate_id": sim.get("candidate_id"),
                "ai_score": ai_score,
                "human_score": human_score,
                "score_gap": gap,
                "ai_decision": ai_decision,
                "human_decision": human_decision,
                "decisions_aligned": aligned,
                "discrepancy_note": discrepancy_note,
            })

        total = max(1, len(comparisons))
        alignment_rate = round((decision_matches / total) * 100.0, 2)
        avg_gap = round(sum(gaps) / total, 2) if gaps else 0.0

        return {
            "total_evaluated": len(comparisons),
            "decision_alignment_rate_percent": alignment_rate,
            "average_score_gap": avg_gap,
            "max_score_gap": max(gaps) if gaps else 0.0,
            "comparisons": comparisons,
        }


system_simulation_pipeline = SystemSimulationPipeline()
