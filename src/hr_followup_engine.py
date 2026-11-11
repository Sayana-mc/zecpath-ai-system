"""Day 34: Dynamic Follow-Up Logic and Adaptive Questioning Engine."""

import uuid
from typing import Any

from src import database


class HRFollowUpEngine:
    """Detects answer quality and generates tailored follow-up questions."""

    VAGUE_PATTERNS = [
        "i don't know",
        "i dont know",
        "not sure",
        "not really sure",
        "maybe",
        "nothing much",
        "no idea",
        "i cannot say",
        "kind of",
        "sort of",
    ]

    def __init__(self, max_followups_per_question: int = 1):
        self.max_followups = max_followups_per_question

    def detect_response_quality(self, response_text: str) -> str:
        """Categorize candidate response quality into incomplete, vague, or complete."""
        if not response_text or not response_text.strip():
            return "incomplete"

        cleaned = response_text.strip().lower()
        words = cleaned.split()

        if any(pat in cleaned for pat in self.VAGUE_PATTERNS):
            return "vague"

        if len(words) <= 4:
            return "incomplete"

        return "complete"

    def determine_difficulty_level(self, response_text: str, confidence_level: str = "normal") -> str:
        """Adapts question difficulty level based on response richness and confidence."""
        if not response_text or not response_text.strip():
            return "simple"

        words = len(response_text.split())
        if confidence_level == "high" and words >= 15:
            return "advanced"
        if confidence_level == "high" or words >= 10:
            return "medium"
        return "simple"

    def evaluate_and_generate_followup(
        self,
        interview_id: str,
        question_id: str,
        question_text: str,
        candidate_response: str,
        confidence_level: str = "normal",
    ) -> dict[str, Any]:
        """Evaluates candidate response and generates an adaptive follow-up if appropriate."""
        quality = self.detect_response_quality(candidate_response)

        # Check existing follow-ups for this parent question
        existing_followups = [
            f for f in database.list_hr_interview_followups(interview_id)
            if f["parent_question_id"] == question_id
        ]

        if len(existing_followups) >= self.max_followups:
            return {
                "needs_followup": False,
                "quality": quality,
                "followup": None,
                "reason": "Maximum follow-ups reached for this question.",
            }

        difficulty = self.determine_difficulty_level(candidate_response, confidence_level)

        if quality == "incomplete":
            followup_type = "clarification"
            followup_text = (
                f"Could you please elaborate a little more on your answer to: \"{question_text}\"?"
            )
        elif quality == "vague":
            followup_type = "example_based"
            followup_text = (
                "Could you provide a specific example from your experience to illustrate that point?"
            )
        elif difficulty == "advanced":
            followup_type = "scenario_based"
            followup_text = (
                "That is a great overview. Can you describe a challenging scenario you encountered while doing that, and how you resolved it?"
            )
        else:
            followup_type = "deepening"
            followup_text = (
                "Can you walk me through your specific contribution and the key decisions you made during that process?"
            )

        followup_id = f"HRFU_{uuid.uuid4().hex[:8].upper()}"
        followup_record = {
            "followup_id": followup_id,
            "interview_id": interview_id,
            "parent_question_id": question_id,
            "followup_type": followup_type,
            "followup_question": followup_text,
            "candidate_response": None,
            "difficulty_level": difficulty,
        }
        saved_followup = database.save_hr_interview_followup(interview_id, followup_record)

        return {
            "needs_followup": True,
            "needed": True,
            "quality": quality,
            "type": followup_type,
            "followup": saved_followup,
            "reason": f"Response categorized as {quality}; triggered {followup_type} follow-up.",
        }


hr_followup_engine = HRFollowUpEngine()

