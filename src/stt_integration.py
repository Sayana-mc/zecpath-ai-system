"""Speech-to-text integration for the root application."""

import os
import uuid
from pathlib import Path
from typing import Any

from day24_speech_to_text.src.stt_processor import SpeechToTextProcessor
from day24_speech_to_text.src.transcript_normalizer import normalize_transcription

from . import database
from .schemas import (
    ScreeningAudioUploadResponse,
    ScreeningAudioStatusResponse,
    ScreeningTranscriptCreate,
    ScreeningTranscriptResponse,
)

UPLOAD_DIR = Path(__file__).resolve().parents[1] / "uploads" / "screening_audio"
MAX_AUDIO_BYTES = 50 * 1024 * 1024
ALLOWED_AUDIO_TYPES = {
    ".wav": {"audio/wav", "audio/x-wav"},
    ".mp3": {"audio/mpeg"},
    ".m4a": {"audio/mp4", "audio/x-m4a"},
    ".ogg": {"audio/ogg"},
    ".flac": {"audio/flac"},
}


class STTIntegration:
    """Wrapper for STT processing with provider abstraction."""

    def __init__(self):
        provider = os.environ.get("STT_PROVIDER", "faster_whisper")
        self.processor = SpeechToTextProcessor(provider=provider)

    def validate_audio_file(self, file_path: Path, file_size: int, mime_type: str) -> None:
        """Validate audio file type, size, and format."""
        extension = file_path.suffix.lower()
        if extension not in ALLOWED_AUDIO_TYPES:
            raise ValueError(f"Unsupported audio format: {extension}")

        if file_size > MAX_AUDIO_BYTES:
            raise ValueError(f"Audio file too large: {file_size} bytes exceeds {MAX_AUDIO_BYTES} byte limit")

        if mime_type and mime_type not in ALLOWED_AUDIO_TYPES[extension]:
            raise ValueError(f"MIME type {mime_type} does not match extension {extension}")

    def transcribe_audio(self, audio_path: Path, timeout_seconds: int = 60) -> dict[str, Any]:
        """Transcribe audio file and return normalized result."""
        stt_result = self.processor.transcribe(str(audio_path), timeout_seconds=timeout_seconds)
        normalized = normalize_transcription(stt_result)
        return {
            "stt_result": stt_result,
            "normalized": normalized,
        }

    async def upload_audio(
        self,
        session_id: str,
        file_bytes: bytes,
        filename: str,
        mime_type: str,
        question_id: str | None = None,
    ) -> ScreeningAudioUploadResponse:
        """Save uploaded audio file and create database record."""
        extension = Path(filename).suffix.lower()
        audio_id = str(uuid.uuid4())
        file_path = UPLOAD_DIR / f"{audio_id}{extension}"
        UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
        file_path.write_bytes(file_bytes)

        audio_record = {
            "audio_id": audio_id,
            "session_id": session_id,
            "question_id": question_id,
            "file_path": str(file_path),
            "file_size_bytes": len(file_bytes),
            "duration_seconds": None,
            "mime_type": mime_type,
            "source": "UPLOAD",
        }
        database.save_screening_audio(session_id, audio_record)
        return ScreeningAudioUploadResponse(
            audio_id=audio_id,
            session_id=session_id,
            question_id=question_id,
            status="PENDING",
            message="Audio uploaded successfully. Ready for transcription.",
        )

    def process_audio(self, audio_id: str) -> ScreeningTranscriptResponse:
        """Process audio file through STT and save transcript."""
        audio = database.get_screening_audio(audio_id)
        if not audio:
            raise ValueError("Audio record not found")

        database.update_screening_audio_status(audio_id, "PROCESSING")

        try:
            result = self.transcribe_audio(Path(audio["file_path"]))
            stt_result = result["stt_result"]
            normalized = result["normalized"]

            transcript_id = str(uuid.uuid4())
            transcript = ScreeningTranscriptCreate(
                audio_id=audio_id,
                question_id=audio.get("question_id"),
                raw_text=normalized["raw_text"],
                cleaned_text=normalized["clean_text"],
                language=normalized["language"],
                language_probability=normalized["language_probability"],
                partial_answer=normalized["partial_answer"],
                segment_count=normalized["segment_count"],
                processing_version="stt-v1",
            )

            saved = database.save_screening_transcript(audio["session_id"], transcript.model_dump())
            database.update_screening_audio_status(audio_id, "COMPLETED")
            return ScreeningTranscriptResponse(**saved)

        except Exception as exc:
            database.update_screening_audio_status(audio_id, "FAILED")
            raise

    def get_audio_status(self, audio_id: str) -> ScreeningAudioStatusResponse:
        """Get audio processing status."""
        audio = database.get_screening_audio(audio_id)
        if not audio:
            raise ValueError("Audio record not found")
        return ScreeningAudioStatusResponse(**audio)

    def get_transcript(self, transcript_id: str) -> ScreeningTranscriptResponse:
        """Get transcript by ID."""
        transcript = database.get_screening_transcript(transcript_id)
        if not transcript:
            raise ValueError("Transcript not found")
        return ScreeningTranscriptResponse(**transcript)


stt_integration = STTIntegration()