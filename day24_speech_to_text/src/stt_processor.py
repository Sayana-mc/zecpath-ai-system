import json
from pathlib import Path

from faster_whisper import WhisperModel


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONFIG_DIR = PROJECT_ROOT / "config"


def load_config():
    with open(CONFIG_DIR / "stt_config.json", "r", encoding="utf-8") as f:
        return json.load(f)


class SpeechToTextProcessor:
    def __init__(self):
        self.config = load_config()

        self.model = WhisperModel(
            self.config["model_size"],
            device=self.config["device"],
            compute_type=self.config["compute_type"]
        )

    def transcribe(self, audio_path):
        audio_path = Path(audio_path)

        if not audio_path.exists():
            raise FileNotFoundError(
                f"Audio file not found: {audio_path}"
            )

        segments, info = self.model.transcribe(
            str(audio_path),
            language=self.config["language"],
            beam_size=self.config["beam_size"],
            vad_filter=self.config["vad_filter"],
            vad_parameters={
                "min_silence_duration_ms":
                    self.config["vad_min_silence_duration_ms"]
            }
        )

        segment_data = []
        full_text = []

        for segment in segments:
            text = segment.text.strip()

            if not text:
                continue

            segment_data.append({
                "start": round(segment.start, 2),
                "end": round(segment.end, 2),
                "text": text
            })

            full_text.append(text)

        return {
            "language": info.language,
            "language_probability": round(
                info.language_probability, 4
            ),
            "text": " ".join(full_text).strip(),
            "segments": segment_data
        }