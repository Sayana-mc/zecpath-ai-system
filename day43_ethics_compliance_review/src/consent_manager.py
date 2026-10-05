from typing import Dict


class ConsentManager:
    def __init__(self, config: Dict):
        self.config = config

    def validate_consent(self, consent_given: bool) -> Dict:
        required = self.config["consent"]["required"]

        if required and not consent_given:
            return {
                "status": "BLOCKED",
                "consent_valid": False,
                "message": "Candidate consent is required before AI processing."
            }

        return {
            "status": "ALLOWED",
            "consent_valid": True,
            "message": "Candidate consent requirement satisfied."
        }