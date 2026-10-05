import re
from typing import Dict, List


class BiasSignalDetector:

    def __init__(self, config: Dict):
        self.signals = [
            signal.lower()
            for signal in config["demographic_signals"]
        ]

    def detect(self, text: str) -> Dict:
        text_lower = text.lower()
        detected: List[str] = []

        for signal in self.signals:
            pattern = r"\b" + re.escape(signal) + r"\b"

            if re.search(pattern, text_lower):
                detected.append(signal)

        return {
            "bias_signals_detected": detected,
            "bias_signal_count": len(detected),
            "clean": len(detected) == 0
        }

    def remove_signals(self, text: str) -> Dict:
        cleaned_text = text
        removed = []

        for signal in self.signals:
            pattern = r"\b" + re.escape(signal) + r"\b"

            if re.search(pattern, cleaned_text, flags=re.IGNORECASE):
                removed.append(signal)
                cleaned_text = re.sub(
                    pattern,
                    "[REMOVED]",
                    cleaned_text,
                    flags=re.IGNORECASE
                )

        return {
            "original_text": text,
            "cleaned_text": cleaned_text,
            "removed_signals": removed
        }