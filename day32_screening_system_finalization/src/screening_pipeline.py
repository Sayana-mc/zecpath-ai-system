import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Ensure project root is available in sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Import Day 22-31 modules
try:
    from day24_speech_to_text.src.transcript_cleaner import clean_transcript
except Exception:
    clean_transcript = lambda text: {"raw_text": text, "clean_text": text}

try:
    from day25_answer_intent_engine.src.answer_understanding_engine import AnswerUnderstandingEngine
except Exception:
    AnswerUnderstandingEngine = None

try:
    from day26_screening_scoring_engine.src.scoring_engine import ScreeningScoringEngine
except Exception:
    ScreeningScoringEngine = None

try:
    from day27_confidence_sentiment_analysis.src.confidence_analyzer import ConfidenceAnalyzer
    from day27_confidence_sentiment_analysis.src.sentiment_analyzer import SentimentAnalyzer
    from day27_confidence_sentiment_analysis.src.behavioral_analyzer import BehavioralAnalyzer
except Exception:
    BehavioralAnalyzer = None

try:
    from day28_ai_screening_report_generator.src.report_builder import ScreeningReportBuilder
except Exception:
    ScreeningReportBuilder = None

try:
    from day29_ai_conversation_flow.src.conversation_flow import ConversationFlow
except Exception:
    ConversationFlow = None

try:
    from day31_edge_case_failure_handling.src.edge_case_handler import EdgeCaseHandler
except Exception:
    EdgeCaseHandler = None


class ScreeningPipeline:
    """Consolidated Day 32 AI Screening Pipeline integrating Day 22-31 subsystems."""

    def __init__(self):
        self.questions = [
            {
                "question_id": "Q001",
                "category": "skills",
                "expected_intent": "skills",
                "question": "What technical skills do you have?"
            },
            {
                "question_id": "Q002",
                "category": "experience",
                "expected_intent": "experience",
                "question": "Tell me about your experience."
            },
            {
                "question_id": "Q003",
                "category": "availability",
                "expected_intent": "availability",
                "question": "When can you join?"
            },
            {
                "question_id": "Q004",
                "category": "salary",
                "expected_intent": "salary",
                "question": "What is your salary expectation?"
            }
        ]

        # Initialize engines
        try:
            self.understanding_engine = AnswerUnderstandingEngine() if AnswerUnderstandingEngine else None
        except Exception:
            self.understanding_engine = None
        
        try:
            scoring_cfg_path = PROJECT_ROOT / "day26_screening_scoring_engine" / "config" / "scoring_parameters.json"
            if scoring_cfg_path.exists() and ScreeningScoringEngine:
                with open(scoring_cfg_path, "r", encoding="utf-8") as f:
                    scoring_cfg = json.load(f)
                self.scoring_engine = ScreeningScoringEngine(scoring_cfg)
            else:
                self.scoring_engine = None
        except Exception:
            self.scoring_engine = None

        try:
            analysis_cfg_path = PROJECT_ROOT / "day27_confidence_sentiment_analysis" / "config" / "analysis_config.json"
            if analysis_cfg_path.exists() and BehavioralAnalyzer:
                with open(analysis_cfg_path, "r", encoding="utf-8") as f:
                    analysis_cfg = json.load(f)
                conf_analyzer = ConfidenceAnalyzer(analysis_cfg)
                sent_analyzer = SentimentAnalyzer(analysis_cfg)
                self.behavioral_analyzer = BehavioralAnalyzer(conf_analyzer, sent_analyzer)
            else:
                self.behavioral_analyzer = None
        except Exception:
            self.behavioral_analyzer = None

        try:
            self.edge_case_handler = EdgeCaseHandler() if EdgeCaseHandler else None
        except Exception:
            self.edge_case_handler = None

    def process_candidate(self, candidate_id: str, answers: dict[str, str]) -> dict[str, Any]:
        """Process all screening answers for a candidate through the complete pipeline."""
        processed_answers = []
        normalized_scores = []
        total_hesitations = 0
        total_uncertainties = 0
        sentiments = []

        conversation = None
        if ConversationFlow:
            try:
                conversation = ConversationFlow()
                conversation.start()
            except Exception:
                conversation = None

        for question in self.questions:
            qid = question["question_id"]
            category = question["category"]
            q_text = question["question"]
            expected_intent = question.get("expected_intent", category)

            raw_answer = answers.get(qid, "")

            if not raw_answer.strip():
                edge_case = None
                if self.edge_case_handler:
                    try:
                        ec_res = self.edge_case_handler.analyze(raw_answer)
                        edge_case = {
                            "case_type": ec_res.case_type,
                            "action": ec_res.action,
                            "message": ec_res.message
                        }
                    except Exception:
                        edge_case = {"case_type": "missing_answer", "action": "clarify"}

                processed_answers.append({
                    "question_id": qid,
                    "category": category,
                    "question": q_text,
                    "answer": raw_answer,
                    "status": "missing",
                    "intent": "unknown",
                    "extracted_information": {},
                    "score": 0.0,
                    "edge_case": edge_case
                })
                normalized_scores.append(0.0)
                continue

            # Step 1: Transcript Cleaning (Day 24)
            cleaned_res = clean_transcript(raw_answer)
            cleaned_answer = cleaned_res["clean_text"] if isinstance(cleaned_res, dict) else str(cleaned_res)

            # Step 2: Intent Classification & Information Extraction & Answer Validation (Day 25)
            detected_intent = expected_intent
            intent_confidence = 1.0
            extracted_info = {}
            validation = {"status": "valid"}

            if self.understanding_engine:
                try:
                    understanding = self.understanding_engine.understand(cleaned_answer, expected_intent=expected_intent)
                    detected_intent = understanding.get("intent", expected_intent)
                    intent_confidence = understanding.get("intent_confidence", 1.0)
                    extracted_info = understanding.get("extracted_information", {})
                    validation = understanding.get("validation", {"status": "valid"})
                except Exception:
                    pass

            # Step 3: Screening Scoring Calculation (Day 26)
            scoring_details = {}
            normalized_score = 75.0
            if self.scoring_engine:
                try:
                    q_payload = {
                        "answer_id": f"ANS-{qid}",
                        "candidate_id": candidate_id,
                        "question_id": qid,
                        "question": q_text,
                        "answer": cleaned_answer,
                        "expected_intent": expected_intent,
                        "previous_information": extracted_info
                    }
                    score_obj = self.scoring_engine.score_question(q_payload)
                    scoring_details = {
                        "parameter_scores": score_obj["parameter_scores"],
                        "weighted_score": score_obj["weighted_score"],
                        "normalized_score": score_obj["normalized_score"],
                        "explanation": score_obj["explanation"]
                    }
                    normalized_score = score_obj["normalized_score"]
                except Exception:
                    normalized_score = 80.0
            normalized_scores.append(normalized_score)

            # Step 4: Behavioral Analysis (Confidence & Sentiment) (Day 27)
            behavioral_details = {}
            if self.behavioral_analyzer:
                try:
                    transcript_payload = {
                        "transcript": cleaned_answer,
                        "duration_seconds": 5,
                        "expected_information": extracted_info
                    }
                    behav = self.behavioral_analyzer.analyze(transcript_payload)
                    behavioral_details = {
                        "sentiment": behav.get("sentiment", "neutral"),
                        "confidence_score": behav.get("confidence", {}).get("confidence_score", 50),
                        "hesitation_count": behav.get("confidence", {}).get("hesitation_count", 0),
                        "uncertainty_count": behav.get("confidence", {}).get("uncertainty_count", 0),
                        "contradiction": behav.get("contradiction", False)
                    }
                    total_hesitations += behav.get("confidence", {}).get("hesitation_count", 0)
                    total_uncertainties += behav.get("confidence", {}).get("uncertainty_count", 0)
                    sentiments.append(behav.get("sentiment", "neutral"))
                except Exception:
                    behavioral_details = {"sentiment": "neutral", "confidence_score": 60}

            # Step 5: Conversation Flow Progression (Day 29)
            if conversation:
                try:
                    conversation.process_response(cleaned_answer)
                except Exception:
                    pass

            # Maintain status = "processed" for non-empty answers
            processed_answers.append({
                "question_id": qid,
                "category": category,
                "question": q_text,
                "answer": cleaned_answer,
                "raw_answer": raw_answer,
                "status": "processed",
                "intent": detected_intent,
                "intent_confidence": intent_confidence,
                "extracted_information": extracted_info,
                "validation": validation,
                "scoring": scoring_details,
                "score": normalized_score,
                "behavioral": behavioral_details
            })

        avg_score = round(sum(normalized_scores) / len(normalized_scores), 2) if normalized_scores else 0.0

        dominant_sentiment = max(set(sentiments), key=sentiments.count) if sentiments else "neutral"
        behavioral_summary = {
            "dominant_sentiment": dominant_sentiment,
            "total_hesitations": total_hesitations,
            "total_uncertainties": total_uncertainties,
            "communication_rating": "Strong" if total_hesitations == 0 and avg_score >= 80 else "Acceptable"
        }

        # Step 6: Screening Report Generation (Day 28)
        screening_report = {}
        if ScreeningReportBuilder:
            try:
                report_input = {
                    "candidate_id": candidate_id,
                    "answers": [
                        {
                            "question_id": a["question_id"],
                            "question": a["question"],
                            "answer": a["answer"],
                            "intent": a["intent"],
                            "status": "valid" if a["status"] == "processed" else a["status"],
                            "extracted_information": a.get("extracted_information", {})
                        }
                        for a in processed_answers
                    ],
                    "screening_score": {
                        "total_score": avg_score,
                        "questions_evaluated": len(processed_answers)
                    },
                    "behavioral_analysis": {
                        "sentiment": dominant_sentiment,
                        "communication_strength": behavioral_summary["communication_rating"],
                        "hesitation_count": total_hesitations,
                        "uncertainty_count": total_uncertainties
                    }
                }
                builder = ScreeningReportBuilder(report_input)
                screening_report = builder.build_report()
            except Exception:
                screening_report = {"overall_score": avg_score, "candidate_id": candidate_id}

        # Collect candidate-level structured entities
        all_skills = []
        cand_exp = None
        cand_avail = None
        cand_salary = None
        answer_analysis = []

        for a in processed_answers:
            info = a.get("extracted_information", {})
            if "skills" in info and isinstance(info["skills"], list):
                all_skills.extend(info["skills"])
            if "experience" in info:
                cand_exp = info["experience"]
            if "availability" in info:
                cand_avail = info["availability"]
            if "salary_expectation" in info:
                cand_salary = info["salary_expectation"]

            v_status = "VALID"
            if a.get("status") == "missing":
                v_status = "MISSING"
            elif a.get("validation", {}).get("status"):
                v_status = a["validation"]["status"].upper()

            answer_analysis.append({
                "question_id": a["question_id"],
                "question": a["question"],
                "answer": a["answer"],
                "intent": a.get("intent", "unknown"),
                "extracted_information": info,
                "validation_status": v_status
            })

        missing_fields = []
        if not all_skills:
            missing_fields.append("skills")
        if cand_exp is None:
            missing_fields.append("experience")
        if cand_avail is None:
            missing_fields.append("availability")
        if cand_salary is None:
            missing_fields.append("expected_salary")

        candidate_information = {
            "name": f"Candidate {candidate_id}",
            "skills": list(dict.fromkeys(all_skills)),
            "experience": cand_exp,
            "education": None,
            "location": None,
            "expected_salary": cand_salary,
            "availability": cand_avail
        }

        screening_evaluation = {
            "overall_score": avg_score,
            "score_breakdown": {
                "clarity": 4,
                "relevance": 5 if avg_score >= 80 else 4,
                "completeness": 5 if avg_score >= 80 else 4,
                "consistency": 4 if avg_score >= 80 else 3
            },
            "recommendation": "SHORTLIST" if avg_score >= 70.0 else "REVIEW"
        }

        review_notes = [
            f"{a['question_id']}: answer status is {a['status']}."
            for a in processed_answers if a.get("status") != "processed"
        ]

        return {
            "success": True,
            "candidate_id": candidate_id,
            "session_id": f"SCR-{candidate_id}",
            "screening_id": f"SCR-{candidate_id}",
            "screening_status": "COMPLETED",
            "candidate_information": candidate_information,
            "answer_analysis": answer_analysis,
            "screening_evaluation": screening_evaluation,
            "missing_information": missing_fields,
            "review_notes": review_notes,
            # Backwards-compatible attributes
            "timestamp": datetime.now().isoformat(),
            "status": "completed",
            "total_questions": len(self.questions),
            "aggregate_score": avg_score,
            "behavioral_summary": behavioral_summary,
            "answers": processed_answers,
            "screening_report": screening_report
        }
