from transcript_cleaner import (
    clean_transcript,
    detect_partial_answer
)


def normalize_transcription(stt_result):

    raw_text = stt_result["text"]
    segments = stt_result["segments"]

    cleaned = clean_transcript(raw_text)

    partial_answer = detect_partial_answer(
        cleaned["clean_text"],
        segments
    )

    return {
        "raw_text": raw_text,
        "clean_text": cleaned["clean_text"],
        "language": stt_result["language"],
        "language_probability":
            stt_result["language_probability"],
        "segments": segments,
        "partial_answer": partial_answer,
        "segment_count": len(segments)
    }