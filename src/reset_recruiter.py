"""Reset the single recruiter account using a salted PBKDF2 password hash."""

from getpass import getpass

from src import database
from .auth import hash_recruiter_password


def main() -> None:
    database.initialize_database()
    username = input("New recruiter username: ").strip()
    if not username or len(username) > 160:
        raise SystemExit("Username must contain 1 to 160 characters.")

    password = getpass("New recruiter password (at least 16 characters): ")
    confirmation = getpass("Confirm new recruiter password: ")
    if len(password) < 16:
        raise SystemExit("Password must contain at least 16 characters.")
    if password != confirmation:
        raise SystemExit("Passwords do not match.")

    password_salt, password_hash = hash_recruiter_password(password)
    try:
        database.reset_recruiter_account(username, password_salt, password_hash)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc

    print("Recruiter credentials reset. Existing sessions have been revoked.")


if __name__ == "__main__":
    main()
