from intent_classifier import IntentClassifier
from information_extractor import extract_information
from answer_validator import validate_answer


class AnswerUnderstandingEngine:

    def __init__(self):

        self.classifier = IntentClassifier()

    def understand(
        self,
        answer,
        expected_intent=None
    ):

        classification = self.classifier.classify(
            answer
        )

        detected_intent = classification["intent"]

        intent_for_validation = (
            expected_intent
            if expected_intent
            else detected_intent
        )

        validation = validate_answer(
            answer,
            intent_for_validation
        )

        information = extract_information(
            detected_intent,
            answer
        )

        return {
            "intent": detected_intent,
            "intent_confidence":
                classification["confidence"],
            "answer_status":
                validation["status"],
            "validation": validation,
            "extracted_information": information
        }