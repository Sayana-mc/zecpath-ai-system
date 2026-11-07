import hashlib
import hmac
import secrets

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from . import database


_basic_auth = HTTPBasic(auto_error=False)
SESSION_COOKIE_NAME = "zecpath_session"
SESSION_LIFETIME_SECONDS = 8 * 60 * 60
PASSWORD_HASH_ITERATIONS = 600_000
PASSWORD_SALT_BYTES = 16


def authentication_is_configured() -> bool:
    return database.has_recruiter_accounts()


def hash_recruiter_password(password: str) -> tuple[str, str]:
    salt = secrets.token_bytes(PASSWORD_SALT_BYTES)
    password_hash = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt, PASSWORD_HASH_ITERATIONS
    )
    return salt.hex(), password_hash.hex()


def is_configured_recruiter(username: str) -> bool:
    return database.get_recruiter_account(username) is not None


def verify_recruiter_credentials(username: str, password: str) -> str | None:
    account = database.get_recruiter_account(username)
    salt = (
        bytes.fromhex(account["password_salt"])
        if account
        else bytes(PASSWORD_SALT_BYTES)
    )
    expected = bytes.fromhex(account["password_hash"]) if account else bytes(32)
    supplied = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        PASSWORD_HASH_ITERATIONS,
    )
    if account and hmac.compare_digest(supplied, expected):
        return account["username"]
    return None


def require_recruiter(
    request: Request,
    credentials: HTTPBasicCredentials | None = Depends(_basic_auth),
) -> str:
    if not authentication_is_configured():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Recruiter authentication is not configured.",
        )

    session_token = request.cookies.get(SESSION_COOKIE_NAME)
    if session_token:
        session_username = database.get_recruiter_session(session_token)
        if session_username is None or not is_configured_recruiter(session_username):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Recruiter session expired. Sign in again.",
            )
        if request.method not in {"GET", "HEAD", "OPTIONS"}:
            expected_origin = f"{request.url.scheme}://{request.url.netloc}"
            if request.headers.get("origin") != expected_origin:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="A same-origin request is required for this session.",
                )
        return session_username

    supplied_username = credentials.username if credentials else ""
    supplied_password = credentials.password if credentials else ""
    verified_username = verify_recruiter_credentials(
        supplied_username, supplied_password
    )
    if verified_username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Valid recruiter credentials are required.",
            headers={"WWW-Authenticate": "Basic"},
        )
    return verified_username
