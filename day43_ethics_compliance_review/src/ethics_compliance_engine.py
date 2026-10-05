from typing import Dict, List

from .consent_manager import ConsentManager
from .bias_signal_detector import BiasSignalDetector
from .fairness_reviewer import FairnessReviewer
from .explainability import ExplainabilityGenerator
from .retention_manager import RetentionManager


class EthicsComplianceEngine:

    def __init__(self, config: Dict):
        self.consent_manager = ConsentManager(config)
        self.bias_detector = BiasSignalDetector(config)
        self.fairness_reviewer = FairnessReviewer(config)
        self.explainability = ExplainabilityGenerator()
        self.retention_manager = RetentionManager(config)

    def review_candidate(
        self,
        candidate: Dict,
        consent_given: bool,
        created_at: str
    ) -> Dict:

        consent_result = self.consent_manager.validate_consent(
            consent_given
        )

        bias_result = self.bias_detector.detect(
            candidate.get("response_text", "")
        )

        cleaned_result = self.bias_detector.remove_signals(
            candidate.get("response_text", "")
        )

        explanation = self.explainability.generate(candidate)

        retention = self.retention_manager.calculate_expiry(
            created_at
        )

        return {
            "candidate_id": candidate.get("candidate_id"),
            "consent_review": consent_result,
            "bias_review": bias_result,
            "bias_signal_removal": cleaned_result,
            "explainability": explanation,
            "retention": retention
        }

    def review_fairness(
        self,
        candidates: List[Dict]
    ) -> Dict:

        return self.fairness_reviewer.review_scores(candidates)