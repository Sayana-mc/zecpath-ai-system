import json
import re
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = PROJECT_ROOT / "config"


KNOWN_SKILLS = [
    "python",
    "sql",
    "excel",
    "power bi",
    "tableau",
    "r",
    "sas",
    "java",
    "javascript",
    "react",
    "node.js",
    "c++",
    "c#",
    "tensorflow",
    "pytorch",
    "pandas",
    "numpy",
    "scikit-learn",
    "mongodb",
    "mysql",
    "git",
    "github",
]


def load_intent_config():
    config_file = CONFIG_DIR / "intent_config.json"

    with open(config_file, "r", encoding="utf-8") as file:
        return json.load(file)


class IntentClassifier:

    def __init__(self):
        self.config = load_intent_config()

    def _normalize(self, text):
        text = str(text or "").lower().strip()
        text = text.replace("'", "")
        return re.sub(r"\s+", " ", text)

    def _has_skill_mentions(self, text):
        matches = []

        for skill in KNOWN_SKILLS:
            if skill == "r":
                pattern = r"(?<![a-z0-9_])r(?![a-z0-9_])"
            else:
                pattern = r"(?<!\w)" + re.escape(skill) + r"(?!\w)"

            if re.search(pattern, text):
                matches.append(skill)

        return matches

    def classify(self, answer):
        text = self._normalize(answer)

        if not text:
            return {
                "intent": "missing",
                "confidence": 1.0
            }

        skill_matches = self._has_skill_mentions(text)
        if skill_matches:
            return {
                "intent": "skills",
                "confidence": 1.0
            }

        if re.search(r"\b(?:salary|expected salary|salary expectation|ctc|package|compensation|pay|lpa|inr|rupees)\b", text):
            return {
                "intent": "salary_expectation",
                "confidence": 1.0
            }

        if re.search(r"\b(?:available|availability|join|joining|notice period|immediately|immediate|when can you join)\b", text):
            return {
                "intent": "availability",
                "confidence": 1.0
            }

        if re.search(r"\b\d+(?:\.\d+)?\s*(?:year|years|yr|yrs|month|months)\b", text) or re.search(r"\b(?:experience|worked|working|internship|internships|work experience)\b", text):
            return {
                "intent": "experience",
                "confidence": 1.0
            }

        scores = {intent: 0 for intent in self.config["intents"]}
        for intent, keywords in self.config["intents"].items():
            for keyword in keywords:
                if keyword.lower() in text:
                    scores[intent] += 1

        if not any(scores.values()):
            return {
                "intent": "unknown",
                "confidence": 0.0
            }

        best_intent, best_score = max(scores.items(), key=lambda item: item[1])
        total_score = sum(scores.values())
        confidence = round(best_score / total_score, 2) if total_score else 0.0

        return {
            "intent": best_intent,
            "confidence": confidence
        }