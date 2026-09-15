import re


class AnswerValidator:
    """
    Validates candidate answers for:
    - Missing answers
    - Vague answers
    - Off-topic answers
    """


    # --------------------------------------------------------
    # VAGUE ANSWERS
    # --------------------------------------------------------

    VAGUE_RESPONSES = {
        "",
        "i don't know",
        "i dont know",
        "don't know",
        "dont know",
        "not sure",
        "no idea",
        "maybe",
        "nothing",
        "none",
        "no",
        "n/a",
        "na"
    }


    # --------------------------------------------------------
    # OFF-TOPIC KEYWORDS
    # --------------------------------------------------------

    OFF_TOPIC_KEYWORDS = {
        "movie",
        "movies",
        "film",
        "films",
        "game",
        "games",
        "gaming",
        "cricket",
        "football",
        "music",
        "song",
        "songs",
        "travel",
        "travelling",
        "traveling",
        "cooking",
        "dance",
        "dancing",
        "shopping",
        "hobby",
        "hobbies"
    }


    # --------------------------------------------------------
    # NORMALIZATION
    # --------------------------------------------------------

    def _normalize(self, text):

        if text is None:
            return ""

        text = str(text).strip().lower()

        # Keep apostrophes so:
        # "I don't know." -> "i don't know"
        text = re.sub(
            r"[^\w\s']",
            "",
            text
        )

        # Remove extra spaces
        text = re.sub(
            r"\s+",
            " ",
            text
        )

        return text.strip()


    # --------------------------------------------------------
    # VAGUE DETECTION
    # --------------------------------------------------------

    def _is_vague(self, normalized_text):

        if normalized_text in self.VAGUE_RESPONSES:
            return True

        return False


    # --------------------------------------------------------
    # OFF-TOPIC DETECTION
    # --------------------------------------------------------

    def _is_off_topic(self, normalized_text):

        words = set(
            normalized_text.split()
        )

        return bool(
            words.intersection(
                self.OFF_TOPIC_KEYWORDS
            )
        )


    # --------------------------------------------------------
    # VALIDATE ANSWER
    # --------------------------------------------------------

    def validate(
        self,
        answer,
        expected_intent=None
    ):

        normalized_text = self._normalize(
            answer
        )

        # Empty answer
        if not normalized_text:

            return {
                "missing": True,
                "vague": False,
                "off_topic": False,
                "status": "missing"
            }


        # Vague answer
        if self._is_vague(
            normalized_text
        ):

            return {
                "missing": False,
                "vague": True,
                "off_topic": False,
                "status": "vague"
            }


        # Off-topic answer
        if self._is_off_topic(
            normalized_text
        ):

            return {
                "missing": False,
                "vague": False,
                "off_topic": True,
                "status": "off_topic"
            }


        # Valid answer
        return {
            "missing": False,
            "vague": False,
            "off_topic": False,
            "status": "valid"
        }


# ============================================================
# BACKWARD-COMPATIBLE FUNCTION
# ============================================================

def validate_answer(
    answer,
    expected_intent=None
):

    validator = AnswerValidator()

    return validator.validate(
        answer,
        expected_intent=expected_intent
    )