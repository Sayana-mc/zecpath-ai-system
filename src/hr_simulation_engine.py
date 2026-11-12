"""Day 40: HR Interview Simulation, Benchmarking, and Human-vs-AI Evaluation."""

import uuid
from typing import Any

try:
    from . import database
except ImportError:
    from src import database
from .hr_interview_engine import hr_interview_engine
from .hr_followup_engine import hr_followup_engine
from .hr_communication_evaluator import hr_communication_evaluator
from .hr_confidence_analyzer import hr_confidence_analyzer
from .hr_scoring_engine import hr_scoring_engine
from .hr_aptitude_engine import hr_aptitude_engine
from .hr_summary_generator import hr_summary_generator


SYNTHETIC_CANDIDATE_PERSONAS = {
    "confident": {
        "candidate_id": "SIM_CONFIDENT",
        "name": "Arjun Patel",
        "experience_level": "EXPERIENCED",
        "role_type": "TECHNICAL",
        "answers": {
            "SELF_INTRODUCTION": "I am a Senior Backend Engineer with 5 years of experience architecting high-throughput distributed systems in Python and Go.",
            "CAREER_JOURNEY": "I began as a junior developer optimizing database queries, and progressively led core infrastructure scaling at my previous company.",
            "STRENGTHS_WEAKNESSES": "My greatest strength is systematic architectural problem solving. My growth area is learning to delegate earlier in project cycles.",
            "TEAMWORK": "I mentor junior developers and conduct cross-functional backlog grooming to ensure alignment across engineering and product.",
            "CULTURE_FIT": "I thrive in an open, high-ownership engineering culture with clear deliverables and blameless post-mortems.",
            "CAREER_GOALS": "Over the next three years, I aim to grow into a Principal Engineer driving system reliability and platform scalability.",
            "AVAILABILITY_COMMITMENT": "I am serving a 30-day notice period and am fully committed to joining your engineering team.",
            "ROLE_BASED_TECHNICAL": "I redesigned an async message pipeline using Redis and PostgreSQL, reducing latency by 45% and eliminating connection pool saturation.",
        },
    },
    "hesitant": {
        "candidate_id": "SIM_HESITANT",
        "name": "Maya Sharma",
        "experience_level": "FRESHER",
        "role_type": "TECHNICAL",
        "answers": {
            "SELF_INTRODUCTION": "Um, hello... I am a fresh graduate, I think, and I studied computer science and basic web development.",
            "CAREER_JOURNEY": "Well, maybe... I worked on a few college projects with Python, but I am still not completely sure about industry practices.",
            "STRENGTHS_WEAKNESSES": "I guess my strength is that I try hard... my weakness is, you know, feeling nervous in technical discussions.",
            "TEAMWORK": "Um, I can work with a team, I suppose.",
            "CULTURE_FIT": "I just want a peaceful workplace, basically.",
            "CAREER_GOALS": "I don't know for sure, maybe grow as a developer.",
            "AVAILABILITY_COMMITMENT": "I can join immediately, I think.",
            "ROLE_BASED_TECHNICAL": "I fixed some bugs in my college project when the code had errors.",
        },
    },
    "inexperienced": {
        "candidate_id": "SIM_INEXPERIENCED",
        "name": "Rohan Gupta",
        "experience_level": "FRESHER",
        "role_type": "NON_TECHNICAL",
        "answers": {
            "SELF_INTRODUCTION": "I recently graduated in Business Administration with coursework in operations and project tracking.",
            "CAREER_JOURNEY": "During college, I coordinated the annual student festival and led logistics for university events.",
            "STRENGTHS_WEAKNESSES": "I am very organized and proactive. I need more hands-on experience with enterprise CRM software.",
            "TEAMWORK": "I enjoyed collaborating with my peers to divide event duties and ensure on-time delivery.",
            "CULTURE_FIT": "I look for a supportive team where mentorship and learning are prioritized.",
            "CAREER_GOALS": "I want to become an effective project coordinator over the next two years.",
            "AVAILABILITY_COMMITMENT": "I am available to start immediately.",
            "ROLE_BASED_NON_TECHNICAL": "I coordinated weekly student meetings and handled scheduling conflicts by listening to both sides.",
        },
    },
    "contradictory": {
        "candidate_id": "SIM_CONTRADICTORY",
        "name": "Vikram Singh",
        "experience_level": "EXPERIENCED",
        "role_type": "TECHNICAL",
        "answers": {
            "SELF_INTRODUCTION": "I have 6 years of solid full-stack engineering experience building web apps.",
            "CAREER_JOURNEY": "I have been in tech for only 2 years working on basic frontend scripts.",
            "STRENGTHS_WEAKNESSES": "My strength is speed. My weakness is attention to documentation.",
            "TEAMWORK": "I usually prefer working alone without team syncs.",
            "CULTURE_FIT": "I am adaptable.",
            "CAREER_GOALS": "To earn more.",
            "AVAILABILITY_COMMITMENT": "Immediately available.",
            "ROLE_BASED_TECHNICAL": "I wrote code for several websites.",
        },
    },
}


class HRInterviewSimulator:
    """Simulates realistic end-to-end HR interview sessions for QA and calibration."""

    def simulate_interview(
        self,
        candidate_type: str = "EXPERIENCED",
        role_type: str = "TECHNICAL",
        persona: str = "confident",
        opening_id: str | None = None,
    ) -> dict[str, Any]:
        """Convenience method to simulate an interview session."""
        op_id = opening_id or f"sim_op_{uuid.uuid4().hex[:6]}"
        return self.simulate_candidate_session(persona_key=persona, opening_id=op_id)

    def compare_human_ai_evaluations(
        self,
        ai_score: float,
        human_score: float,
    ) -> dict[str, Any]:
        """Compares AI scoring with human rubric and calculates alignment delta / agreement rate."""
        diff = round(abs(ai_score - human_score), 2)
        agreement = "HIGH" if diff <= 10.0 else "MODERATE" if diff <= 20.0 else "DIVERGENT"
        return {
            "ai_score": ai_score,
            "human_score": human_score,
            "score_difference": diff,
            "agreement_level": agreement,
        }

    def simulate_candidate_session(
        self,
        persona_key: str,
        opening_id: str,
    ) -> dict[str, Any]:
        """Runs a complete synthetic interview simulation for a persona."""
        persona = SYNTHETIC_CANDIDATE_PERSONAS.get(persona_key, SYNTHETIC_CANDIDATE_PERSONAS["confident"])

        # Ensure synthetic opening and candidate exist in DB
        if not database.get_opening(opening_id):
            database.create_opening({
                "opening_id": opening_id,
                "title": f"Simulated {persona.get('role_type', 'TECHNICAL')} Role",
                "description": "Simulation opening",
                "required_skills": ["Communication", "Problem Solving"],
                "preferred_skills": [],
                "minimum_education": "BACHELORS",
                "minimum_years_experience": 1,
            })
        if not database.get_candidate(persona["candidate_id"]):
            database.create_candidate({
                "candidate_id": persona["candidate_id"],
                "name": persona["name"],
                "email": f"{persona_key}@simulation.local",
                "opening_id": opening_id,
                "skills": ["Communication", "Teamwork"],
                "resume_text": "Simulated candidate profile.",
            })

        # 1. Create Session
        created = hr_interview_engine.create_interview_session(
            candidate_id=persona["candidate_id"],
            opening_id=opening_id,
            experience_level=persona["experience_level"],
            role_type=persona["role_type"],
            recruiter_id="simulation-recruiter",
        )
        interview_id = created["session"]["interview_id"]
        questions = created["questions"]

        # 2. Start Session
        hr_interview_engine.start_interview(interview_id)

        # 3. Simulate Responses & Evaluations
        captured_responses = []
        for q in questions:
            cat = q["category"]
            answer = persona["answers"].get(
                cat,
                "I am eager to contribute effectively and demonstrate my professional capabilities.",
            )

            # Record response
            quality = hr_followup_engine.detect_response_quality(answer)
            resp_record = {
                "response_id": f"HRRSP_{uuid.uuid4().hex[:8].upper()}",
                "interview_id": interview_id,
                "question_id": q["question_id"],
                "raw_response": answer,
                "cleaned_response": answer,
                "quality": quality,
                "follow_up_eligible": q.get("follow_up_eligibility", True),
                "follow_up_count": 0,
            }
            saved_resp = database.save_hr_interview_response(interview_id, resp_record)
            captured_responses.append(saved_resp)

            # Communication evaluation
            hr_communication_evaluator.evaluate_communication(
                interview_id=interview_id,
                text=answer,
                response_id=saved_resp["response_id"],
            )

            # Behavioral signals
            hr_confidence_analyzer.analyze_signals(
                interview_id=interview_id,
                text=answer,
                response_id=saved_resp["response_id"],
                previous_answers=captured_responses[:-1],
            )

        # 4. Simulate an Aptitude Question
        apt_q = hr_aptitude_engine.get_questions()[0]
        apt_answer = (
            "First, calculate the total high-priority tasks (4). Then subtract the 3 completed ones, "
            "so 1 task remains, which equals 25% of the high-priority tasks."
            if persona_key == "confident"
            else "1 task remains."
        )
        hr_aptitude_engine.evaluate_and_save(
            interview_id=interview_id,
            question_id=apt_q["question_id"],
            candidate_answer=apt_answer,
        )

        # 5. Calculate Score & Generate Summary Report
        score = hr_scoring_engine.calculate_session_score(
            interview_id=interview_id,
            candidate_id=persona["candidate_id"],
        )

        report = hr_summary_generator.generate_and_save_report(interview_id)

        return {
            "interview_id": interview_id,
            "persona": persona_key,
            "score": score,
            "report": report,
        }


hr_simulation_engine = HRInterviewSimulator()

