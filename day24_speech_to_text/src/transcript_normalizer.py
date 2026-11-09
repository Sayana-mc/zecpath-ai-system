from .transcript_cleaner import (
    clean_transcript,
    detect_partial_answer
)


def normalize_transcription(stt_result):
    if not stt_result:
        return {
            "raw_text": "",
            "clean_text": "",
            "language": "unknown",
            "language_probability": 0.0,
            "segments": [],
            "partial_answer": True,
            "segment_count": 0
        }

    raw_text = str(stt_result.get("text", "")).strip()
    segments = stt_result.get("segments") or []
    backup_language = stt_result.get("language", "unknown")
    backup_probability = stt_result.get("language_probability", 0.0)

    cleaned = clean_transcript(raw_text)

    partial_answer = detect_partial_answer(
        cleaned["clean_text"],
        segments
    )

    return {
        "raw_text": raw_text,
        "clean_text": cleaned["clean_text"],
        "language": backup_language,
        "language_probability": backup_probability,
        "segments": segments,
        "partial_answer": partial_answer,
        "segment_count": len(segments)
    }