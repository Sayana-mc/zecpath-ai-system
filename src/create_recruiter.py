"""Initialize the first recruiter account using a salted PBKDF2 password hash."""

from getpass import getpass

from . import database
from .auth import hash_recruiter_password


def main() -> None:
    database.initialize_database()
    if database.has_recruiter_accounts():
        raise SystemExit(
            "A recruiter account is already initialized. No changes were made."
        )

    username = input("Recruiter username: ").strip()
    if not username or len(username) > 160:
        raise SystemExit("Username must contain 1 to 160 characters.")

    password = getpass("Recruiter password (at least 16 characters): ")
    confirmation = getpass("Confirm recruiter password: ")
    if len(password) < 16:
        raise SystemExit("Password must contain at least 16 characters.")
    if password != confirmation:
        raise SystemExit("Passwords do not match.")

    password_salt, password_hash = hash_recruiter_password(password)
    try:
        database.create_first_recruiter_account(
            username, password_salt, password_hash
        )
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc

    print("First recruiter account initialized. The password is not stored in plaintext.")


if __name__ == "__main__":
    main()
