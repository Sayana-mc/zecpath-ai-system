import base64
import json
import os
import secrets
from pathlib import Path
from cryptography.fernet import Fernet, InvalidToken
from .security_errors import StorageKeyError


def load_or_create_key(env_name: str = "ZECpath_STORAGE_KEY") -> bytes:
    """
    For local demos only, generates a key if missing and prints it once.
    Production: inject a managed secret from a vault/KMS; never print or commit keys.
    """
    existing = os.environ.get(env_name)
    if existing:
        try:
            key = existing.encode("ascii")
            Fernet(key)
            return key
        except Exception as exc:
            raise StorageKeyError(f"{env_name} is not a valid Fernet key.") from exc

    key = Fernet.generate_key()
    os.environ[env_name] = key.decode("ascii")
    print(f"[DEMO ONLY] Generated storage key for this process. Save securely outside source control:\n{key.decode('ascii')}")
    print("For subsequent runs, set the environment variable before starting the app.")
    return key


class SecureFileStore:
    """Encrypts payloads at rest using Fernet (AES-128-CBC + HMAC-SHA256)."""

    def __init__(self, directory: str | Path, key: bytes):
        try:
            self.fernet = Fernet(key)
        except Exception as exc:
            raise StorageKeyError("Invalid encryption key.") from exc
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)

    def put(self, record_id: str, category: str, content: str) -> dict:
        if not record_id or not category or not isinstance(content, str):
            raise ValueError("record_id, category, and string content are required.")
        safe_id = "".join(c for c in record_id if c.isalnum() or c in "-_")
        if not safe_id:
            raise ValueError("record_id must contain letters or numbers.")
        encrypted = self.fernet.encrypt(content.encode("utf-8"))
        path = self.directory / f"{safe_id}.enc"
        path.write_bytes(encrypted)
        metadata = {
            "record_id": safe_id,
            "category": category,
            "encrypted": True,
            "updated_at": __import__("datetime").datetime.now(
                __import__("datetime").timezone.utc
            ).isoformat()
        }
        # Metadata is non-sensitive; content is encrypted.
        (self.directory / f"{safe_id}.meta.json").write_text(
            json.dumps(metadata, indent=2), encoding="utf-8"
        )
        return metadata

    def get(self, record_id: str) -> str:
        safe_id = "".join(c for c in record_id if c.isalnum() or c in "-_")
        path = self.directory / f"{safe_id}.enc"
        if not path.exists():
            raise FileNotFoundError(safe_id)
        try:
            return self.fernet.decrypt(path.read_bytes()).decode("utf-8")
        except InvalidToken as exc:
            raise StorageKeyError("Decryption failed: key is wrong or data was modified.") from exc

    def delete(self, record_id: str) -> bool:
        safe_id = "".join(c for c in record_id if c.isalnum() or c in "-_")
        removed = False
        for suffix in (".enc", ".meta.json"):
            path = self.directory / f"{safe_id}{suffix}"
            if path.exists():
                path.unlink()
                removed = True
        return removed
