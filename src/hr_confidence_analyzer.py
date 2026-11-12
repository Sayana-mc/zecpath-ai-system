"""Day 36: Confidence, Uncertainty, and Behavioral Signal Analysis."""

import re
import uuid
from typing import Any

try:
    from . import database
except ImportError:
    from src import database


class HRConfidenceAnalyzer:
    """Analyzes candidate response signals for hesitation, uncertainty, sentiment, and contradiction."""

    HESITATION_PHRASES = [
        "um",
        "uh",
        "hmm",
        "actually",
        "well",
        "let me think",
    ]

    UNCERTAINTY_PHRASES = [
        "i think",
        "maybe",
        "perhaps",
        "probably",
        "i am not sure",
        "not sure",
        "i guess",
        "might be",
        "i don't know",
        "i dont know",
    ]

    PAUSE_MARKERS = [
        "...",
        "[pause]",
        "[long pause]",
        "<pause>",
    ]

    POSITIVE_WORDS = [
        "successfully",
        "achieved",
        "improved",
        "excelled",
        "enjoyed",
        "productive",
        "effective",
        "passionate",
        "collaborative",
        "growth",
    ]

    NEGATIVE_WORDS = [
        "failed",
        "conflict",
        "frustrated",
        "difficult",
        "disagreed",
        "stressful",
        "unable",
        "disliked",
    ]

    DISCLAIMER = (
        "Behavioral signals reflect observable communication markers (fillers, qualifiers, pacing). "
        "They do NOT constitute psychological diagnosis, emotion evaluation, or internal stress measurement."
    )

    def detect_hesitation(self, text: str) -> dict[str, Any]:
        lowered = text.lower()
        hesitation_count = sum(lowered.count(phrase) for phrase in self.HESITATION_PHRASES)
        pause_count = sum(text.count(marker) for marker in self.PAUSE_MARKERS)
        return {
            "hesitation_count": hesitation_count,
            "pause_count": pause_count,
            "detected": (hesitation_count + pause_count) > 0,
        }

    def detect_uncertainty(self, text: str) -> dict[str, Any]:
        lowered = text.lower()
        count = sum(lowered.count(phrase) for phrase in self.UNCERTAINTY_PHRASES)
        return {
            "uncertainty_count": count,
            "detected": count > 0,
        }

    def detect_repeated_words(self, text: str) -> dict[str, Any]:
        words = re.findall(r"\b[a-zA-Z]+\b", text.lower())
        repeats = 0
        for i in range(len(words) - 1):
            if words[i] == words[i + 1]:
                repeats += 1
        return {
            "repeated_word_count": repeats,
            "detected": repeats > 0,
        }

    def analyze_sentiment(self, text: str) -> dict[str, Any]:
        lowered = text.lower()
        pos = sum(1 for w in self.POSITIVE_WORDS if w in lowered)
        neg = sum(1 for w in self.NEGATIVE_WORDS if w in lowered)
        if pos > 0 and neg > 0:
            return {"sentiment": "MIXED", "score": 0.0}
        if pos > neg:
            return {"sentiment": "POSITIVE", "score": min(1.0, pos * 0.3)}
        if neg > pos:
            return {"sentiment": "NEGATIVE", "score": -min(1.0, neg * 0.3)}
        return {"sentiment": "NEUTRAL", "score": 0.0}

    def detect_contradiction(
        self,
        current_answer: str,
        previous_answers: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Compares current statement with past captured facts to flag factual discrepancies."""
        if not previous_answers:
            return {"contradiction": False, "reason": None}

        current_lower = current_answer.lower()
        # Check experience years mismatch
        years_current = re.findall(r"(\d+)\s+(?:year|years)", current_lower)
        if years_current:
            curr_y = int(years_current[0])
            for prev in previous_answers:
                prev_text = prev.get("cleaned_response", prev.get("raw_response", "")).lower()
                prev_years = re.findall(r"(\d+)\s+(?:year|years)", prev_text)
                if prev_years:
                    prev_y = int(prev_years[0])
                    if abs(curr_y - prev_y) >= 2:
                        return {
                            "contradiction": True,
                            "reason": f"Discrepancy in stated experience duration: {curr_y} years vs previously stated {prev_y} years.",
                        }

        # Check direct assertion vs denial
        for prev in previous_answers:
            prev_text = prev.get("cleaned_response", prev.get("raw_response", "")).lower()
            if "never" in current_lower and ("experience" in prev_text or "worked with" in prev_text or "managed" in prev_text):
                return {
                    "contradiction": True,
                    "reason": "Direct contradiction detected: earlier statement claimed experience while current response claims never having worked with it.",
                }
        return {"contradiction": False, "reason": None}

    def analyze_signals(
        self,
        interview_id: str,
        text: str,
        response_id: str | None = None,
        previous_answers: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Performs full behavioral signal analysis and persists results."""
        hesitation = self.detect_hesitation(text)
        uncertainty = self.detect_uncertainty(text)
        repeats = self.detect_repeated_words(text)
        sentiment_res = self.analyze_sentiment(text)
        contradiction = self.detect_contradiction(text, previous_answers)

        # Baseline confidence score calculation (0 - 100)
        base_confidence = 85.0
        base_confidence -= hesitation["hesitation_count"] * 5.0
        base_confidence -= hesitation["pause_count"] * 10.0
        base_confidence -= uncertainty["uncertainty_count"] * 8.0
        base_confidence -= repeats["repeated_word_count"] * 5.0
        if contradiction["contradiction"]:
            base_confidence -= 20.0
        confidence_score = max(20.0, min(100.0, base_confidence))

        # Stress / uncertainty indicator score
        stress_score = (
            (hesitation["hesitation_count"] * 10.0)
            + (hesitation["pause_count"] * 15.0)
            + (uncertainty["uncertainty_count"] * 15.0)
            + (repeats["repeated_word_count"] * 10.0)
        )
        stress_score = min(100.0, stress_score)

        signal_id = f"HRSIG_{uuid.uuid4().hex[:8].upper()}"
        signals_record = {
            "signal_id": signal_id,
            "interview_id": interview_id,
            "response_id": response_id,
            "hesitation_count": hesitation["hesitation_count"],
            "pause_count": hesitation["pause_count"],
            "uncertainty_count": uncertainty["uncertainty_count"],
            "repeated_word_count": repeats["repeated_word_count"],
            "sentiment": sentiment_res["sentiment"],
            "sentiment_score": sentiment_res["score"],
            "stress_score": stress_score,
            "confidence_score": confidence_score,
            "contradiction_detected": 1 if contradiction["contradiction"] else 0,
            "contradiction_reason": contradiction["reason"],
            "contradictions_detected": [contradiction["reason"]] if contradiction["contradiction"] else [],
            "disclaimer": self.DISCLAIMER,
            "ethical_disclaimer": self.DISCLAIMER,
        }
        saved = database.save_hr_behavioral_signals(interview_id, signals_record)
        return saved


hr_confidence_analyzer = HRConfidenceAnalyzer()

