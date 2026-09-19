from dataclasses import dataclass, asdict


@dataclass
class EdgeCaseResult:
    case_type: str
    severity: str
    action: str
    message: str
    retry_allowed: bool


class EdgeCaseHandler:
    """
    Detects common screening-call edge cases and
    provides retry / clarification / safe fallback actions.
    """

    def analyze(
        self,
        transcript,
        confidence=1.0,
        language="en",
        background_noise=False
    ):
        text = (transcript or "").strip()

        # Missing answer
        if not text:
            return self._result(
                "missing_answer",
                "medium",
                "clarify",
                "I didn't receive an answer. Could you please answer the question?",
                True
            )

        # Poor audio / low STT confidence
        if confidence < 0.50:
            return self._result(
                "poor_audio",
                "high",
                "retry",
                "I'm sorry, I couldn't hear that clearly. Could you please repeat your answer?",
                True
            )

        # Background noise
        if background_noise:
            return self._result(
                "background_noise",
                "medium",
                "retry",
                "There seems to be some background noise. Could you please repeat your answer clearly?",
                True
            )

        # Language mixing
        mixed_language_words = [
            "hai", "haina", "cheyyam", "cheyyunnu",
            "venam", "illa", "aane", "aanu"
        ]

        words = text.lower().split()

        if language == "mixed" or any(
            word in mixed_language_words for word in words
        ):
            return self._result(
                "language_mixing",
                "low",
                "clarify",
                "I noticed mixed-language speech. Could you please answer clearly in one language?",
                True
            )

        # Very short / incomplete answer
        if len(words) <= 2:
            return self._result(
                "incomplete_answer",
                "medium",
                "clarify",
                "Could you please provide a little more detail?",
                True
            )

        # Safe fallback
        return self._result(
            "normal",
            "none",
            "continue",
            "Thank you. Let's continue with the next question.",
            False
        )

    def _result(
        self,
        case_type,
        severity,
        action,
        message,
        retry_allowed
    ):
        return EdgeCaseResult(
            case_type=case_type,
            severity=severity,
            action=action,
            message=message,
            retry_allowed=retry_allowed
        )

    def analyze_as_dict(
        self,
        transcript,
        confidence=1.0,
        language="en",
        background_noise=False
    ):
        result = self.analyze(
            transcript,
            confidence,
            language,
            background_noise
        )

        return asdict(result)