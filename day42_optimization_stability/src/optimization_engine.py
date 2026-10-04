import time


class OptimizationEngine:

    def __init__(
        self,
        transcript_cleaner,
        followup_stabilizer,
        scoring_engine
    ):
        self.transcript_cleaner = (
            transcript_cleaner
        )

        self.followup_stabilizer = (
            followup_stabilizer
        )

        self.scoring_engine = (
            scoring_engine
        )

        self.cache = {}

    def clean_transcript(self, text):

        if text in self.cache:
            return self.cache[text]

        cleaned = (
            self.transcript_cleaner.clean(text)
        )

        self.cache[text] = cleaned

        return cleaned

    def optimize_interview(
        self,
        sample
    ):

        start_time = time.perf_counter()

        raw_response = sample.get(
            "response",
            ""
        )

        cleaned_response = (
            self.clean_transcript(
                raw_response
            )
        )

        previous_score = (
            sample.get(
                "previous_score",
                50
            )
        )

        previous_score = (
            self.scoring_engine.validate_score(
                previous_score
            )
        )

        previous_followups = []

        followup = (
            self.followup_stabilizer.select_followup(
                cleaned_response,
                previous_followups
            )
        )

        if followup:
            previous_followups.append(
                followup
            )

        processing_time = (
            time.perf_counter()
            - start_time
        )

        return {
            "candidate_id": sample.get(
                "candidate_id"
            ),
            "question_id": sample.get(
                "question_id"
            ),
            "original_response": raw_response,
            "cleaned_response": cleaned_response,
            "previous_score": previous_score,
            "followup_question": followup,
            "followup_count": len(
                previous_followups
            ),
            "processing_time_ms": round(
                processing_time * 1000,
                4
            )
        }