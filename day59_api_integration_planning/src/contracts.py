class ContractError(ValueError):
    pass

def require_string(data, field):
    value = data.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ContractError(f"{field} must be a non-empty string")
    return value.strip()

def validate_resume_request(data):
    for field in ("candidate_id", "document_uri", "idempotency_key"):
        require_string(data, field)
    if data.get("document_type") not in {"pdf", "docx"}:
        raise ContractError("document_type must be pdf or docx")

def validate_interview_request(data):
    for field in ("candidate_id", "interview_id", "question_id", "rubric_version"):
        require_string(data, field)
    transcript = data.get("transcript_text")
    if not isinstance(transcript, str) or not transcript.strip():
        raise ContractError("transcript_text must be non-empty")
    if len(transcript) > 20000:
        raise ContractError("transcript_text too long")

def validate_score_response(data):
    score = data.get("score")
    if isinstance(score, bool) or not isinstance(score, (int, float)) or not 0 <= score <= 100:
        raise ContractError("score must be between 0 and 100")
    if data.get("review_required") is not True:
        raise ContractError("review_required must be true")
