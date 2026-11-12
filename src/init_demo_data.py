"""ZecPath AI Hiring System - Repeatable Demo Data Initialization Script

Day 63: Seeds a complete, realistic, multi-round synthetic dataset into the database
for live demonstrations, system validation, and recruiter dashboard walkthroughs.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any

try:
    from . import database
except ImportError:
    from src import database
from .services import calculate_candidate_match
from .coaching_engine import generate_candidate_coaching
from .cross_round_scoring_engine import calculate_cross_round_score
from .final_recommendation_engine import generate_final_recommendation
from .hiring_intelligence_report_generator import generate_candidate_hiring_report
from .observability import observability
from .resume_analysis import extract_resume_data

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger("zecpath.init_demo")

ROOT_DIR = Path(__file__).resolve().parents[1]
DEMO_DIR = ROOT_DIR / "demo_data"


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def seed_demo_environment(target_db: str | None = None, reset: bool = False) -> dict[str, Any]:
    """Populates the database with realistic synthetic demo data."""
    if target_db:
        os.environ["ZECPATH_DB_PATH"] = str(target_db)

    database.initialize_database()

    logger.info("Starting ZecPath Demo Data Seeding...")

    # 1. Load Job Openings
    jobs_dir = DEMO_DIR / "jobs"
    openings_map: dict[str, dict[str, Any]] = {}
    if jobs_dir.exists():
        for job_file in sorted(jobs_dir.glob("*.json")):
            data = load_json(job_file)
            job_key = job_file.stem
            op = database.save_opening(
                title=data["title"],
                description=data["description"],
                requirements=data["required_skills"],
                preferred_skills=data.get("preferred_skills", []),
                minimum_education=data.get("minimum_education"),
                minimum_years_experience=data.get("minimum_years_experience", 0.0),
                status="OPEN",
            )
            openings_map[job_key] = op
            logger.info(f"Seeded Opening: {op['title']} ({op['opening_id']})")

    # Ensure a default opening if none loaded
    if not openings_map:
        op = database.save_opening(
            title="Senior Python Backend Architect",
            description="Lead backend architecture and microservices.",
            requirements=["Python", "FastAPI", "PostgreSQL", "Docker", "REST API"],
            preferred_skills=["Kubernetes", "Redis"],
        )
        openings_map["job_python_developer"] = op

    # 2. Load Candidates & Resumes
    candidates_file = DEMO_DIR / "candidates" / "candidates.json"
    seeded_candidates = []
    if candidates_file.exists():
        candidates_data = load_json(candidates_file)
        resumes_dir = DEMO_DIR / "resumes"

        for c_data in candidates_data:
            job_key = c_data.get("job_key", "job_python_developer")
            opening = openings_map.get(job_key, list(openings_map.values())[0])

            # Register Candidate
            cand = database.create_candidate(
                name=c_data["name"],
                email=c_data["email"],
                opening_id=opening["opening_id"],
                skills=c_data["skills"],
            )
            cand_id = cand["candidate_id"]

            # Load and parse resume
            resume_filename = c_data.get("resume_file")
            resume_text = ""
            if resume_filename and (resumes_dir / resume_filename).exists():
                resume_text = (resumes_dir / resume_filename).read_text(encoding="utf-8")
            else:
                resume_text = f"{c_data['name']}\nSkills: {', '.join(c_data['skills'])}\nExperience: {c_data.get('experience_years', 3)} years."

            parsed_resume = extract_resume_data(resume_text)
            database.save_candidate_resume(
                candidate_id=cand_id,
                filename=resume_filename or "resume.txt",
                parsed_text=resume_text,
                resume_data=parsed_resume,
            )

            # Compute ATS Score
            cand_dict = {**cand, "skills": c_data["skills"], "resume_text": resume_text}
            match_score, match_evidence = calculate_candidate_match(cand_dict, opening)
            database.save_candidate_score(
                candidate_id=cand_id,
                score=match_score,
                evidence=match_evidence,
            )

            # Evaluate Pre-screening Eligibility
            elig_status = "ELIGIBLE" if "Strong" in c_data.get("archetype", "") or "Partial" in c_data.get("archetype", "") else "REVIEW_REQUIRED"
            database.save_candidate_eligibility_evaluation(
                candidate_id=cand_id,
                opening_id=opening["opening_id"],
                eligibility_status=elig_status,
                failed_thresholds=[] if elig_status == "ELIGIBLE" else ["mandatory_skills"],
                missing_information=[],
                details={"verified_skills": c_data["skills"][:2]},
            )

            # Seed multi-round evaluations for strong or test profiles
            is_strong = "Strong" in c_data.get("archetype", "")
            base_score = 90.0 if is_strong else (75.0 if "Partial" in c_data.get("archetype", "") else 55.0)

            # Screening Session
            database.save_screening_session_full(
                candidate_id=cand_id,
                opening_id=opening["opening_id"],
                overall_score=base_score - 2.0,
                status="COMPLETED",
                summary_notes="Candidate demonstrated structured articulation and technical understanding.",
            )

            # HR Interview Session
            hr_sess = database.create_hr_interview(
                candidate_id=cand_id,
                opening_id=opening["opening_id"],
                candidate_experience_level="EXPERIENCED" if float(c_data.get("experience_years", 0)) >= 3 else "FRESHER",
                overall_score=base_score - 1.0,
                status="COMPLETED",
            )

            # Technical Interview Session
            t_sess = database.create_technical_interview_session(
                candidate_id=cand_id,
                opening_id=opening["opening_id"],
                target_role=opening["title"],
                experience_level="senior" if is_strong else "mid",
            )
            database.save_technical_interview_response({
                "response_id": f"resp_{cand_id[:8]}",
                "interview_id": t_sess["session_id"],
                "question_id": f"q_tech_{cand_id[:6]}",
                "answer_text": "Detailed architectural answer covering connection pooling and idempotency.",
                "score": base_score + 2.0,
                "depth_level": "deep" if is_strong else "moderate",
                "feedback": "Solid answer with clear technical reasoning.",
            })
            database.update_technical_interview_session_status(t_sess["session_id"], "COMPLETED")

            # Machine Test
            m_test = database.create_machine_test_assignment(
                candidate_id=cand_id,
                opening_id=opening["opening_id"],
                task_type="coding",
                task_id="task_01",
                title="Resilient Async Worker",
                description="Implement an asynchronous task queue worker with retry logic.",
            )
            database.save_machine_test_submission({
                "submission_id": f"sub_{cand_id[:8]}",
                "test_id": m_test["assignment_id"],
                "candidate_id": cand_id,
                "code_content": "async def process(): pass",
                "time_spent_minutes": 25.0,
                "total_score": base_score + 1.0,
                "rubric_scores": {"correctness": 95.0, "efficiency": 90.0, "code_quality": 92.0},
                "execution_details": {"passed": True},
            })

            # Cross-Round Score
            cross_eval = calculate_cross_round_score(
                candidate_id=cand_id,
                opening_id=opening["opening_id"],
                target_role=opening["title"],
                round_scores={
                    "ats": match_score,
                    "screening": base_score - 2.0,
                    "hr_interview": base_score - 1.0,
                    "technical_interview": base_score + 2.0,
                    "machine_test": base_score + 1.0,
                },
                save_to_db=True,
            )

            # Final Recommendation
            decision = "SELECTED" if base_score >= 85.0 else ("HOLD_REVIEW" if base_score >= 70.0 else "REJECTED")
            recs = generate_final_recommendation(
                candidate_id=cand_id,
                opening_id=opening["opening_id"],
                target_role=opening["title"],
                decision=decision,
                score=cross_eval["hiring_fit_percentage"],
                save_to_db=True,
            )

            # Hiring Intelligence Report
            report = generate_candidate_hiring_report(candidate_id=cand_id, save_to_db=True)

            # Candidate AI Coaching
            coaching = generate_candidate_coaching(candidate_id=cand_id, save_to_db=True)

            # Decision Audit Log
            observability.log_decision_audit(
                candidate_ref=cand_id,
                opening_ref=opening["opening_id"],
                decision=decision,
                reason=f"Seeded demo candidate: {c_data['archetype']}",
                actor="demo_seeder",
                human_reviewed=True,
            )
            database.append_audit_event(
                event_type="DEMO_CANDIDATE_DECISION",
                actor_id="demo_seeder",
                subject_id=cand_id,
                details={
                    "opening_id": opening["opening_id"],
                    "decision": decision,
                    "fit_score": cross_eval["hiring_fit_percentage"],
                    "archetype": c_data["archetype"],
                },
            )

            seeded_candidates.append({
                "candidate_id": cand_id,
                "name": c_data["name"],
                "role": opening["title"],
                "archetype": c_data["archetype"],
                "ats_score": match_score,
                "fit_score": cross_eval["hiring_fit_percentage"],
                "decision": decision,
                "report_id": report.get("report_id"),
            })
            logger.info(f"Seeded Candidate: {c_data['name']} [{c_data['archetype']}] -> Fit: {cross_eval['hiring_fit_percentage']}% ({decision})")

    logger.info(f"Successfully seeded {len(openings_map)} openings and {len(seeded_candidates)} candidates.")
    return {
        "status": "SUCCESS",
        "openings_count": len(openings_map),
        "candidates_count": len(seeded_candidates),
        "candidates": seeded_candidates,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="ZecPath Demo Data Seeder")
    parser.add_argument("--target-db", help="Path to custom SQLite database file")
    parser.add_argument("--reset", action="store_true", help="Reset existing database before seeding")
    args = parser.parse_args()

    result = seed_demo_environment(target_db=args.target_db, reset=args.reset)
    print("\n" + "=" * 70)
    print("ZECPATH DEMO DATA INITIALIZATION COMPLETE")
    print("=" * 70)
    print(f"Openings Created   : {result['openings_count']}")
    print(f"Candidates Seeded  : {result['candidates_count']}")
    print("\nCandidate Summary:")
    for c in result["candidates"]:
        print(f" - {c['name']:<22} | {c['archetype']:<24} | Fit: {c['fit_score']:>5.1f}% | Decision: {c['decision']}")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
