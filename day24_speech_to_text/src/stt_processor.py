import json
import os
import time
import wave
from pathlib import Path

try:
    from faster_whisper import WhisperModel
except ImportError:  # pragma: no cover - optional dependency for local STT
    WhisperModel = None


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = PROJECT_ROOT / "config"


class _MockSegment:
    def __init__(self, start, end, text):
        self.start = start
        self.end = end
        self.text = text


class _MockInfo:
    def __init__(self, language="en", probability=0.95):
        self.language = language
        self.language_probability = probability


class _MockWhisperModel:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def transcribe(self, audio_path, language=None, beam_size=5, vad_filter=True, vad_parameters=None):
        audio_name = Path(audio_path).stem.replace("_", " ").title()
        fallback_text = (
            "This is a mock transcription generated because no real STT provider "
            "is configured for this environment."
        )

        if audio_name and audio_name.lower() not in {"", "sample", "untitled"}:
            fallback_text = (
                f"This is a mock transcription for {audio_name}. "
                "Real speech-to-text processing requires a configured provider."
            )

        segment = _MockSegment(0.0, 2.5, fallback_text)
        info = _MockInfo(language=language or "en", probability=0.95)
        return [segment], info


def load_config():
    with open(CONFIG_DIR / "stt_config.json", "r", encoding="utf-8") as f:
        return json.load(f)


class SpeechToTextProcessor:
    def __init__(self, config=None, provider=None):
        self.config = load_config()
        if config:
            self.config.update(config)

        self.provider = provider or self.config.get("provider", "mock")
        self.model = self._build_model()

    def _build_model(self):
        if self.provider == "mock":
            return _MockWhisperModel()

        if WhisperModel is None:
            return _MockWhisperModel()

        try:
            return WhisperModel(
                self.config["model_size"],
                device=self.config.get("device", "cpu"),
                compute_type=self.config.get("compute_type", "int8")
            )
        except Exception:
            return _MockWhisperModel()

    def _validate_audio_file(self, audio_path):
        audio_path = Path(audio_path)

        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        if audio_path.suffix.lower() not in {".wav", ".mp3", ".m4a", ".ogg", ".flac"}:
            raise ValueError(f"Unsupported audio format: {audio_path.suffix or 'unknown'}")

        file_size = audio_path.stat().st_size
        max_bytes = self.config.get("max_file_size_bytes", 25 * 1024 * 1024)
        if file_size > max_bytes:
            raise ValueError(
                f"Audio file too large: {file_size} bytes exceeds the configured limit of {max_bytes} bytes."
            )

        duration = self._estimate_duration(audio_path)
        max_duration = self.config.get("max_duration_seconds", 300)
        if duration and duration > max_duration:
            raise ValueError(
                f"Audio file exceeds the supported duration of {max_duration} seconds."
            )

        return audio_path

    def _estimate_duration(self, audio_path):
        if audio_path.suffix.lower() != ".wav":
            return None

        try:
            with wave.open(str(audio_path), "rb") as audio:
                frames = audio.getnframes()
                rate = audio.getframerate()
                if rate <= 0:
                    return None
                return frames / float(rate)
        except Exception:
            return None

    def _mock_transcribe(self, audio_path):
        fallback_text = (
            "This is a mock transcription because no real STT provider is available. "
            "Configure a real provider or install faster-whisper to enable live transcription."
        )

        segment_data = [{
            "start": 0.0,
            "end": 3.0,
            "text": fallback_text
        }]

        return {
            "provider": "mock",
            "status": "mocked",
            "language": self.config.get("language", "en"),
            "language_probability": 0.95,
            "text": fallback_text,
            "segments": segment_data,
            "metadata": {
                "audio_file": str(audio_path),
                "file_size_bytes": audio_path.stat().st_size,
                "duration_seconds": self._estimate_duration(audio_path),
                "provider_status": "mocked"
            }
        }

    def transcribe(self, audio_path, timeout_seconds=30):
        audio_path = self._validate_audio_file(audio_path)

        if self.provider == "mock" or self.model is None or WhisperModel is None:
            return self._mock_transcribe(audio_path)

        try:
            start = time.time()
            segments, info = self.model.transcribe(
                str(audio_path),
                language=self.config.get("language", "en"),
                beam_size=self.config.get("beam_size", 5),
                vad_filter=self.config.get("vad_filter", True),
                vad_parameters={
                    "min_silence_duration_ms": self.config.get("vad_min_silence_duration_ms", 500)
                }
            )

            if time.time() - start > timeout_seconds:
                raise TimeoutError("Speech-to-text provider timed out.")

            segment_data = []
            full_text = []

            for segment in segments:
                text = str(getattr(segment, "text", "")).strip()
                if not text:
                    continue

                segment_data.append({
                    "start": round(float(getattr(segment, "start", 0.0)), 2),
                    "end": round(float(getattr(segment, "end", 0.0)), 2),
                    "text": text
                })
                full_text.append(text)

            return {
                "provider": "faster_whisper",
                "status": "success",
                "language": getattr(info, "language", self.config.get("language", "en")),
                "language_probability": round(float(getattr(info, "language_probability", 0.0)), 4),
                "text": " ".join(full_text).strip(),
                "segments": segment_data,
                "metadata": {
                    "audio_file": str(audio_path),
                    "file_size_bytes": audio_path.stat().st_size,
                    "duration_seconds": self._estimate_duration(audio_path),
                    "provider_status": "success"
                }
            }
        except TimeoutError as exc:
            return {
                "provider": "faster_whisper",
                "status": "timeout",
                "language": self.config.get("language", "en"),
                "language_probability": 0.0,
                "text": "",
                "segments": [],
                "error": str(exc),
                "metadata": {
                    "audio_file": str(audio_path),
                    "file_size_bytes": audio_path.stat().st_size,
                    "duration_seconds": self._estimate_duration(audio_path),
                    "provider_status": "timeout"
                }
            }
        except Exception as exc:
            return {
                "provider": "faster_whisper",
                "status": "error",
                "language": self.config.get("language", "en"),
                "language_probability": 0.0,
                "text": "",
                "segments": [],
                "error": str(exc),
                "metadata": {
                    "audio_file": str(audio_path),
                    "file_size_bytes": audio_path.stat().st_size,
                    "duration_seconds": self._estimate_duration(audio_path),
                    "provider_status": "error"
                }
            }