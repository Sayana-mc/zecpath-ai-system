import re


class TranscriptCleaner:

    FILLER_WORDS = {
        "um",
        "uh",
        "hmm",
        "actually",
        "like"
    }

    def clean(self, text):

        if not text:
            return ""

        text = str(text)

        text = self._normalize_whitespace(text)

        text = self._remove_fillers(text)

        text = self._remove_repeated_words(text)

        text = self._remove_excessive_punctuation(text)

        text = self._normalize_whitespace(text)

        return text.strip()

    def _normalize_whitespace(self, text):

        return re.sub(
            r"\s+",
            " ",
            text
        )

    def _remove_fillers(self, text):

        pattern = (
            r"\b("
            + "|".join(
                re.escape(word)
                for word in self.FILLER_WORDS
            )
            + r")\b"
        )

        return re.sub(
            pattern,
            "",
            text,
            flags=re.IGNORECASE
        )

    def _remove_repeated_words(self, text):

        words = text.split()

        cleaned = []

        previous = None

        for word in words:

            normalized = word.lower().strip(
                ".,!?;"
            )

            if normalized == previous:
                continue

            cleaned.append(word)

            previous = normalized

        return " ".join(cleaned)

    def _remove_excessive_punctuation(self, text):

        text = re.sub(
            r"[!?]{2,}",
            "!",
            text
        )

        text = re.sub(
            r"\.{2,}",
            ".",
            text
        )

        return text