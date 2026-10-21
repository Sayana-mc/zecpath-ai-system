import unittest
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.contracts import ContractError, validate_resume_request, validate_interview_request, validate_score_response
from src.integration_plan import load_config, validate_config, build_plan

class TestDay59(unittest.TestCase):
 def test_config_valid(self): validate_config(load_config())
 def test_human_review_required(self):
  c=load_config(); c["human_review_required"]=False
  with self.assertRaises(ValueError): validate_config(c)
 def test_auto_rejection_disabled(self):
  c=load_config(); c["automatic_rejection_enabled"]=True
  with self.assertRaises(ValueError): validate_config(c)
 def test_resume_async(self):
  c=load_config(); c["resume_processing"]["mode"]="sync"
  with self.assertRaises(ValueError): validate_config(c)
 def test_interview_sync(self):
  c=load_config(); c["interview_scoring"]["mode"]="async"
  with self.assertRaises(ValueError): validate_config(c)
 def test_tls_required(self):
  c=load_config(); c["security"]["tls_required"]=False
  with self.assertRaises(ValueError): validate_config(c)
 def test_resume_valid(self): validate_resume_request({"candidate_id":"C1","document_uri":"https://example.test/a.pdf","document_type":"pdf","idempotency_key":"12345678"})
 def test_resume_missing_candidate(self):
  with self.assertRaises(ContractError): validate_resume_request({"document_uri":"https://example.test/a.pdf","document_type":"pdf","idempotency_key":"12345678"})
 def test_resume_bad_type(self):
  with self.assertRaises(ContractError): validate_resume_request({"candidate_id":"C1","document_uri":"https://example.test/a","document_type":"txt","idempotency_key":"12345678"})
 def test_interview_valid(self): validate_interview_request({"candidate_id":"C1","interview_id":"I1","question_id":"Q1","transcript_text":"SQL joins","rubric_version":"v1"})
 def test_interview_empty(self):
  with self.assertRaises(ContractError): validate_interview_request({"candidate_id":"C1","interview_id":"I1","question_id":"Q1","transcript_text":" ","rubric_version":"v1"})
 def test_interview_too_long(self):
  with self.assertRaises(ContractError): validate_interview_request({"candidate_id":"C1","interview_id":"I1","question_id":"Q1","transcript_text":"x"*20001,"rubric_version":"v1"})
 def test_score_valid(self): validate_score_response({"score":80,"review_required":True})
 def test_score_range(self):
  with self.assertRaises(ContractError): validate_score_response({"score":101,"review_required":True})
 def test_review_required(self):
  with self.assertRaises(ContractError): validate_score_response({"score":80,"review_required":False})
 def test_five_apis(self): self.assertEqual(len(build_plan()["services"]),5)
 def test_retry_policy(self): self.assertEqual(build_plan()["retry_policy"]["max_attempts"],3)
if __name__=="__main__": unittest.main()
