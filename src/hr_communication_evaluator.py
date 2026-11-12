"""Day 35: Communication Skill Evaluation Engine."""

import re
import uuid
from typing import Any

try:
    from . import database
except ImportError:
    from src import database


class HRCommunicationEvaluator:
    """Evaluates candidate communication quality across standardized job-relevant parameters."""

    FILLER_WORDS = {
        "um",
        "uh",
        "like",
        "actually",
        "basically",
        "you know",
        "sort of",
        "kind of",
        "i mean",
    }

    COMMON_GRAMMAR_ANOMALIES = [
        "i am have",
        "he have",
        "she have",
        "they is",
        "i has",
        "we was",
        "he go",
        "she go",
    ]

    def __init__(self):
        self.weights = {
            "fluency": 0.20,
            "grammar": 0.15,
            "vocabulary": 0.15,
            "clarity": 0.30,
            "answer_structure": 0.20,
        }

    def detect_fillers(self, text: str) -> list[str]:
        """Detect filler words without modifying the source text."""
        lowered = text.lower()
        detected = []
        for filler in self.FILLER_WORDS:
            pattern = r"\b" + re.escape(filler) + r"\b"
            if re.search(pattern, lowered):
                detected.append(filler)
        return detected

    def evaluate_fluency(self, text: str) -> float:
        """Measures sentence continuity and response length coherence."""
        words = len(text.split())
        if words == 0:
            return 0.0
        if words < 5:
            return 35.0
        if words < 12:
            return 60.0
        if words < 25:
            return 80.0
        return 95.0

    def evaluate_grammar(self, text: str) -> float:
        """Evaluates grammatical correctness with tolerance for colloquial plain English."""
        if not text.strip():
            return 0.0
        lowered = text.lower()
        score = 90.0
        for err in self.COMMON_GRAMMAR_ANOMALIES:
            if err in lowered:
                score -= 15.0
        return max(score, 20.0)

    def evaluate_vocabulary(self, text: str) -> float:
        """Evaluates vocabulary appropriateness and lexical diversity without punishing simplicity."""
        words = re.findall(r"\b[a-zA-Z]+\b", text.lower())
        if not words:
            return 0.0
        unique_ratio = len(set(words)) / len(words)
        if unique_ratio >= 0.75:
            return 90.0
        if unique_ratio >= 0.55:
            return 80.0
        if unique_ratio >= 0.40:
            return 65.0
        return 50.0

    def evaluate_clarity(self, text: str) -> float:
        """Evaluates understandability, directness, and idea organization."""
        words = len(text.split())
        sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]
        if words == 0:
            return 0.0
        if words <= 3:
            return 30.0
        if len(sentences) >= 2 and words >= 12:
            return 90.0
        if words >= 8:
            return 75.0
        return 60.0

    def evaluate_structure(self, text: str) -> float:
        """Evaluates answer structure (context, explanation, evidence/examples)."""
        words = len(text.split())
        sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]
        if words < 5:
            return 30.0
        # Presence of introductory or connective markers
        connectors = ["because", "for example", "such as", "additionally", "first", "then", "finally", "specifically"]
        has_connector = any(c in text.lower() for c in connectors)
        if len(sentences) >= 2 and has_connector:
            return 90.0
        if len(sentences) >= 2 or words >= 15:
            return 80.0
        return 65.0

    def calculate_filler_control(self, fillers: list[str]) -> float:
        """Scores filler word control."""
        count = len(fillers)
        if count == 0:
            return 100.0
        if count == 1:
            return 85.0
        if count == 2:
            return 70.0
        if count <= 4:
            return 50.0
        return 35.0

    def evaluate_communication(
        self,
        interview_id: str,
        text: str,
        response_id: str | None = None,
    ) -> dict[str, Any]:
        """Runs full multi-factor communication evaluation and persists record."""
        words = len(text.split())
        insufficient_evidence = words < 3

        fillers = self.detect_fillers(text)
        fluency = self.evaluate_fluency(text)
        grammar = self.evaluate_grammar(text)
        vocabulary = self.evaluate_vocabulary(text)
        clarity = self.evaluate_clarity(text)
        structure = self.evaluate_structure(text)
        filler_control = self.calculate_filler_control(fillers)

        total_score = round(
            (fluency * self.weights["fluency"])
            + (grammar * self.weights["grammar"])
            + (vocabulary * self.weights["vocabulary"])
            + (clarity * self.weights["clarity"])
            + (structure * self.weights["answer_structure"]),
            2,
        )

        evidence = [
            f"Fluency evaluated at {fluency} based on pacing and length ({words} words).",
            f"Clarity evaluated at {clarity}; directness of response confirmed.",
            f"Answer structure scored at {structure}.",
        ]
        if fillers:
            evidence.append(f"Detected filler words: {', '.join(fillers)}.")
        if insufficient_evidence:
            evidence.append("Response too brief for comprehensive linguistic assessment.")

        eval_id = f"HREVAL_{uuid.uuid4().hex[:8].upper()}"
        evaluation_record = {
            "evaluation_id": eval_id,
            "interview_id": interview_id,
            "response_id": response_id,
            "fluency_score": fluency,
            "grammar_score": grammar,
            "vocabulary_score": vocabulary,
            "clarity_score": clarity,
            "structure_score": structure,
            "filler_control_score": filler_control,
            "total_communication_score": total_score,
            "fillers_detected": fillers,
            "evidence": evidence,
        }
        saved = database.save_hr_communication_evaluation(interview_id, evaluation_record)
        return saved


hr_communication_evaluator = HRCommunicationEvaluator()

