import json
from pathlib import Path

from .final_hr_scoring_engine import FinalHRScoringEngine
from .interview_evaluator import InterviewEvaluator
from .recommendation_engine import RecommendationEngine


class HRInterviewDemo:

    def __init__(self):
        self.scoring_engine = FinalHRScoringEngine()
        self.evaluator = InterviewEvaluator()
        self.recommendation_engine = RecommendationEngine()

    def load_candidates(self, file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)

    def process_candidate(self, candidate):

        question_results = []

        for item in candidate["responses"]:

            components = self.evaluator.evaluate_response(
                item["response"]
            )

            score = self.scoring_engine.calculate_question_score(
                components["relevance"],
                components["communication"],
                components["confidence"],
                components["consistency"]
            )

            question_results.append({
                "question_id": item["question_id"],
                "question": item["question"],
                "response": item["response"],
                "score_breakdown": score
            })

        hr_score = self.scoring_engine.calculate_candidate_score(
            [
                item["score_breakdown"]
                for item in question_results
            ]
        )

        # Unified score uses the previously defined ATS + Screening + HR stages.
        unified_score = round(
            (candidate["ats_score"] * 0.40)
            + (candidate["screening_score"] * 0.30)
            + (hr_score * 0.30),
            2
        )

        recommendation = (
            self.recommendation_engine
            .get_recommendation(unified_score)
        )

        return {
            "candidate_id": candidate["candidate_id"],
            "candidate_name": candidate["name"],
            "role": candidate["role"],
            "interview": {
                "status": "completed",
                "question_count": len(question_results),
                "question_results": question_results,
                "hr_interview_score": hr_score
            },
            "previous_scores": {
                "ats_score": candidate["ats_score"],
                "screening_score": candidate["screening_score"]
            },
            "final_unified_score": unified_score,
            "final_recommendation": recommendation["recommendation"],
            "recommendation_reason": recommendation["reason"],
            "human_review": True
        }

    def run(self, input_path, output_path):

        candidates = self.load_candidates(input_path)

        results = []

        for candidate in candidates:
            results.append(
                self.process_candidate(candidate)
            )

        output = {
            "system": "HR Interview AI",
            "day": 45,
            "demo_status": "completed",
            "candidate_count": len(results),
            "results": results
        }

        with open(
            output_path,
            "w",
            encoding="utf-8"
        ) as file:
            json.dump(
                output,
                file,
                indent=4
            )

        return output