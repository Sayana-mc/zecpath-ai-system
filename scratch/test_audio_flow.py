import io
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient
from src.main import app
from src import database
from src.auth import hash_recruiter_password
from src.stt_integration import stt_integration
from day24_speech_to_text.src.stt_processor import SpeechToTextProcessor

stt_integration.processor = SpeechToTextProcessor(provider="mock")
salt, password_hash = hash_recruiter_password("test-password-long-enough")
try:
    database.create_first_recruiter_account("test-recruiter-99", salt, password_hash)
except Exception:
    pass

with TestClient(app, headers={"Origin": "http://testserver"}) as client:
    res = client.post("/api/v1/auth/session", json={"username": "test-recruiter-99", "password": "test-password-long-enough"})
    print("Auth:", res.status_code)
    op = client.post("/api/v1/openings", json={"title": "Test Op", "description": "Desc", "required_skills": ["Python"]}).json()
    cand = client.post("/api/v1/candidates", json={"name": "Test", "opening_id": op["opening_id"]}).json()
    sess = client.post("/api/v1/screening/sessions", json={"candidate_id": cand["candidate_id"], "opening_id": op["opening_id"]}).json()
    session_id = sess["session_id"]
    print("Sess:", session_id)
    dummy_wav = b"RIFF" + b"\x00" * 36 + b"WAVEfmt " + b"\x00" * 20 + b"data" + b"\x00" * 100
    upload = client.post(f"/api/v1/screening/sessions/{session_id}/audio", files={"file": ("response.wav", io.BytesIO(dummy_wav), "audio/wav")})
    print("Upload:", upload.status_code, upload.json())
    audio_id = upload.json()["audio_id"]
    tr = client.post(f"/api/v1/screening/audio/{audio_id}/transcribe")
    print("Transcribe:", tr.status_code, tr.json())
