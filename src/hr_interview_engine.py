"""Day 33: HR Interview Engine Architecture and Question Bank."""

import uuid
from typing import Any

from src import database


HR_QUESTION_CATEGORIES = {
    "SELF_INTRODUCTION": {
        "category_id": "CAT_SELF_INTRO",
        "name": "Self Introduction",
        "description": "Candidate introduces themselves, their background and core interests.",
        "evaluation_criteria": ["Clarity of articulation", "Relevant highlights", "Structure"],
    },
    "CAREER_JOURNEY": {
        "category_id": "CAT_CAREER_JOURNEY",
        "name": "Career Journey & Background",
        "description": "Candidate walks through academic or professional milestones and motivation.",
        "evaluation_criteria": ["Career trajectory", "Milestones", "Learning focus"],
    },
    "STRENGTHS_WEAKNESSES": {
        "category_id": "CAT_STRENGTHS_WEAKNESSES",
        "name": "Strengths & Weaknesses",
        "description": "Candidate self-awareness, professional strengths, and growth areas.",
        "evaluation_criteria": ["Self-awareness", "Honesty", "Effort toward improvement"],
    },
    "TEAMWORK": {
        "category_id": "CAT_TEAMWORK",
        "name": "Teamwork & Collaboration",
        "description": "Working with peers, cross-functional collaboration, and conflict resolution.",
        "evaluation_criteria": ["Collaboration examples", "Conflict resolution", "Empathy"],
    },
    "CULTURE_FIT": {
        "category_id": "CAT_CULTURE_FIT",
        "name": "Culture Fit & Workplace Values",
        "description": "Alignment with organization culture, adaptability, and ethical standards.",
        "evaluation_criteria": ["Values alignment", "Adaptability", "Integrity"],
    },
    "CAREER_GOALS": {
        "category_id": "CAT_CAREER_GOALS",
        "name": "Career Goals & Aspiration",
        "description": "Short- and long-term professional aspirations and growth roadmap.",
        "evaluation_criteria": ["Goal clarity", "Realism", "Ambition"],
    },
    "AVAILABILITY_COMMITMENT": {
        "category_id": "CAT_AVAILABILITY",
        "name": "Availability & Commitment",
        "description": "Notice period, joining timeline, work mode, and role commitment.",
        "evaluation_criteria": ["Clarity of timeline", "Commitment to role"],
    },
    "ROLE_BASED_TECHNICAL": {
        "category_id": "CAT_ROLE_TECH",
        "name": "Role-Based Technical Evaluation",
        "description": "Practical application of technical skills and past problem-solving.",
        "evaluation_criteria": ["Technical application", "Problem-solving context"],
    },
    "ROLE_BASED_NON_TECHNICAL": {
        "category_id": "CAT_ROLE_NON_TECH",
        "name": "Role-Based Non-Technical Evaluation",
        "description": "Client interaction, project coordination, and domain engagement.",
        "evaluation_criteria": ["Stakeholder management", "Communication clarity"],
    },
}

QUESTION_BANK_TEMPLATES = [
    # SELF_INTRODUCTION
    {
        "template_id": "TMP_INTRO_01",
        "category": "SELF_INTRODUCTION",
        "question_text": "Please introduce yourself and highlight your academic or professional background.",
        "role_type": "both",
        "experience_level": "both",
        "difficulty": "simple",
        "expected_answer_criteria": "Clear concise introduction with core competencies and education/experience.",
        "follow_up_eligibility": True,
    },
    {
        "template_id": "TMP_INTRO_02",
        "category": "SELF_INTRODUCTION",
        "question_text": "Could you briefly walk me through the key highlights of your resume?",
        "role_type": "both",
        "experience_level": "experienced",
        "difficulty": "simple",
        "expected_answer_criteria": "Structured walkthrough of past roles and major achievements.",
        "follow_up_eligibility": True,
    },
    # CAREER_JOURNEY
    {
        "template_id": "TMP_JOURNEY_FRESHER",
        "category": "CAREER_JOURNEY",
        "question_text": "What motivated you to start your career in this field, and what key academic projects shaped your interest?",
        "role_type": "both",
        "experience_level": "FRESHER",
        "difficulty": "simple",
        "expected_answer_criteria": "Genuine motivation, course projects, or internships that guided career choice.",
        "follow_up_eligibility": True,
    },
    {
        "template_id": "TMP_JOURNEY_EXP",
        "category": "CAREER_JOURNEY",
        "question_text": "Can you walk me through your professional journey and the responsibilities you held in your most recent role?",
        "role_type": "both",
        "experience_level": "EXPERIENCED",
        "difficulty": "medium",
        "expected_answer_criteria": "Career progression, key transitions, leadership/contributor responsibilities.",
        "follow_up_eligibility": True,
    },
    # STRENGTHS_WEAKNESSES
    {
        "template_id": "TMP_STRENGTHS_01",
        "category": "STRENGTHS_WEAKNESSES",
        "question_text": "What do you consider your greatest professional strength, and what is an area you are currently working to improve?",
        "role_type": "both",
        "experience_level": "both",
        "difficulty": "simple",
        "expected_answer_criteria": "Identifies relevant strength with example, and constructive self-improvement step.",
        "follow_up_eligibility": True,
    },
    # TEAMWORK & CULTURE FIT
    {
        "template_id": "TMP_TEAMWORK_01",
        "category": "TEAMWORK",
        "question_text": "Can you describe a time you worked closely with a team to achieve a common goal or resolve a disagreement?",
        "role_type": "both",
        "experience_level": "both",
        "difficulty": "medium",
        "expected_answer_criteria": "Collaboration approach, team dynamic understanding, resolution outcome.",
        "follow_up_eligibility": True,
    },
    {
        "template_id": "TMP_CULTURE_01",
        "category": "CULTURE_FIT",
        "question_text": "What kind of workplace culture and team environment allows you to do your best work?",
        "role_type": "both",
        "experience_level": "both",
        "difficulty": "simple",
        "expected_answer_criteria": "Honest articulation of work style, autonomy vs guidance balance.",
        "follow_up_eligibility": True,
    },
    # CAREER_GOALS
    {
        "template_id": "TMP_GOALS_01",
        "category": "CAREER_GOALS",
        "question_text": "What are your career goals for the next 2 to 3 years, and how does this role fit into that vision?",
        "role_type": "both",
        "experience_level": "both",
        "difficulty": "simple",
        "expected_answer_criteria": "Clear aspirational direction aligned with professional growth.",
        "follow_up_eligibility": True,
    },
    # AVAILABILITY_COMMITMENT
    {
        "template_id": "TMP_AVAIL_01",
        "category": "AVAILABILITY_COMMITMENT",
        "question_text": "What is your current notice period or earliest available joining date, and are you comfortable committing to this role?",
        "role_type": "both",
        "experience_level": "both",
        "difficulty": "simple",
        "expected_answer_criteria": "Specific joining timeline, notice period in days/months, work commitment.",
        "follow_up_eligibility": False,
    },
    # ROLE_BASED_TECHNICAL
    {
        "template_id": "TMP_ROLE_TECH_FRESHER",
        "category": "ROLE_BASED_TECHNICAL",
        "question_text": "Describe a technical challenge or bug you solved while working on a software project or coursework.",
        "role_type": "TECHNICAL",
        "experience_level": "FRESHER",
        "difficulty": "simple",
        "expected_answer_criteria": "Technical debugging, logic explanation, tool/language used.",
        "follow_up_eligibility": True,
    },
    {
        "template_id": "TMP_ROLE_TECH_EXP",
        "category": "ROLE_BASED_TECHNICAL",
        "question_text": "Describe an architectural or technical problem you solved in production, and how you ensured system reliability.",
        "role_type": "TECHNICAL",
        "experience_level": "EXPERIENCED",
        "difficulty": "advanced",
        "expected_answer_criteria": "System architecture, trade-offs, root cause analysis, monitoring.",
        "follow_up_eligibility": True,
    },
    # ROLE_BASED_NON_TECHNICAL
    {
        "template_id": "TMP_ROLE_NON_TECH_01",
        "category": "ROLE_BASED_NON_TECHNICAL",
        "question_text": "Describe a situation where you had to manage conflicting stakeholder expectations or tight delivery deadlines.",
        "role_type": "NON_TECHNICAL",
        "experience_level": "both",
        "difficulty": "medium",
        "expected_answer_criteria": "Stakeholder prioritization, proactive communication, successful delivery.",
        "follow_up_eligibility": True,
    },
]


class RoleBasedQuestionGenerator:
    """Generates personalized HR interview questions based on candidate and opening context."""

    def __init__(self, templates: list[dict[str, Any]] | None = None):
        self.templates = templates or QUESTION_BANK_TEMPLATES

    def generate_questions(
        self,
        experience_level: str = "FRESHER",
        role_type: str = "NON_TECHNICAL",
        opening_title: str | None = None,
        candidate_skills: list[str] | None = None,
    ) -> list[dict[str, Any]]:
        exp = experience_level.upper()
        role = role_type.upper()
        candidate_skills = candidate_skills or []

        selected_questions: list[dict[str, Any]] = []
        categories_seen: set[str] = set()

        for tmpl in self.templates:
            # Experience filter
            tmpl_exp = tmpl["experience_level"].upper()
            if tmpl_exp != "BOTH" and tmpl_exp != exp:
                continue

            # Role type filter
            tmpl_role = tmpl["role_type"].upper()
            if tmpl_role != "BOTH" and tmpl_role != role:
                continue

            cat = tmpl["category"]
            if cat in categories_seen and cat != "ROLE_BASED_TECHNICAL" and cat != "ROLE_BASED_NON_TECHNICAL":
                continue

            question_text = tmpl["question_text"]
            if opening_title and "this role" in question_text:
                question_text = question_text.replace("this role", f"the {opening_title} position")

            categories_seen.add(cat)
            selected_questions.append({
                "template_id": tmpl["template_id"],
                "category": cat,
                "question_text": question_text,
                "role_type": role,
                "experience_level": exp,
                "difficulty": tmpl.get("difficulty", "simple"),
                "expected_answer_criteria": tmpl.get("expected_answer_criteria"),
                "evaluation_parameters": {
                    "clarity": True,
                    "relevance": True,
                    "completeness": True,
                    "consistency": True,
                },
                "follow_up_eligibility": tmpl.get("follow_up_eligibility", True),
                "question_order": len(selected_questions) + 1,
            })

        return selected_questions


class InterviewFlowStateMachine:
    """Manages interview conversation phases and state transitions."""

    PHASES = [
        "CREATED",
        "INTRODUCTION",
        "CORE_HR_QUESTIONS",
        "ROLE_BASED_EVALUATION",
        "CLOSING",
        "COMPLETED",
    ]

    def __init__(self, current_phase: str = "CREATED"):
        self.current_phase = current_phase if current_phase in self.PHASES else "CREATED"

    def transition_to(self, target_phase: str) -> str:
        if target_phase not in self.PHASES:
            raise ValueError(f"Invalid interview phase: {target_phase}")
        self.current_phase = target_phase
        return self.current_phase

    def move_next_phase(self) -> str:
        current_idx = self.PHASES.index(self.current_phase)
        if current_idx < len(self.PHASES) - 1:
            self.current_phase = self.PHASES[current_idx + 1]
        return self.current_phase

    def is_completed(self) -> bool:
        return self.current_phase == "COMPLETED"


class HRInterviewEngine:
    """Core HR Interview Engine managing session initialization and question workflows."""

    def __init__(self):
        self.generator = RoleBasedQuestionGenerator()

    def generate_questions(
        self, experience_level: str = "FRESHER", role_type: str = "NON_TECHNICAL"
    ) -> list[dict[str, Any]]:
        """Convenience method to generate questions for a given experience level and role type."""
        return self.generator.generate_questions(experience_level, role_type)

    def create_interview_session(
        self,
        candidate_id: str,
        opening_id: str,
        experience_level: str = "FRESHER",
        role_type: str = "NON_TECHNICAL",
        recruiter_id: str | None = None,
    ) -> dict[str, Any]:
        """Creates an HR interview session and persists tailored interview questions."""
        candidate = database.get_candidate(candidate_id)
        if not candidate:
            raise ValueError(f"Candidate {candidate_id} not found")

        opening = database.get_opening(opening_id)
        if not opening:
            raise ValueError(f"Opening {opening_id} not found")

        # Infer role type and experience level from opening if needed
        exp = experience_level.upper()
        role = role_type.upper()

        interview_id = str(uuid.uuid4())
        session_data = {
            "interview_id": interview_id,
            "candidate_id": candidate_id,
            "opening_id": opening_id,
            "status": "CREATED",
            "current_phase": "CREATED",
            "current_question_id": None,
            "experience_level": exp,
            "role_type": role,
            "recruiter_id": recruiter_id,
        }
        saved_session = database.create_hr_interview_session(session_data)

        # Generate questions tailored to role & candidate
        generated = self.generator.generate_questions(
            experience_level=exp,
            role_type=role,
            opening_title=opening.get("title"),
            candidate_skills=candidate.get("skills", []),
        )

        persisted_questions: list[dict[str, Any]] = []
        for q in generated:
            q_id = f"HRQ_{uuid.uuid4().hex[:8].upper()}"
            persisted = database.save_hr_interview_question(
                interview_id=interview_id,
                question={
                    "question_id": q_id,
                    "category": q["category"],
                    "question_text": q["question_text"],
                    "role_type": q["role_type"],
                    "experience_level": q["experience_level"],
                    "difficulty": q["difficulty"],
                    "expected_answer_criteria": q["expected_answer_criteria"],
                    "evaluation_parameters": q["evaluation_parameters"],
                    "follow_up_eligibility": q["follow_up_eligibility"],
                    "question_order": q["question_order"],
                    "active_status": True,
                },
            )
            persisted_questions.append(persisted)

        return {
            "session": saved_session,
            "questions": persisted_questions,
        }

    def start_interview(self, interview_id: str) -> dict[str, Any]:
        """Starts an HR interview session, advancing from CREATED to INTRODUCTION."""
        session = database.get_hr_interview_session(interview_id)
        if not session:
            raise ValueError(f"Interview {interview_id} not found")

        questions = database.list_hr_interview_questions(interview_id)
        first_q_id = questions[0]["question_id"] if questions else None

        updated = database.update_hr_interview_session_status(
            interview_id=interview_id,
            status="IN_PROGRESS",
            current_phase="INTRODUCTION",
            current_question_id=first_q_id,
        )
        return {
            "session": updated,
            "current_phase": "INTRODUCTION",
            "current_question": questions[0] if questions else None,
            "message": "Welcome to the HR interview session. Let us begin with your introduction.",
        }


hr_interview_engine = HRInterviewEngine()

