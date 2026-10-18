class SecurityError(Exception):
    """Base class for security and governance failures."""


class AccessDenied(SecurityError):
    """Raised when a user lacks permission for an action."""


class ConsentRequired(SecurityError):
    """Raised when valid consent is missing."""


class IntegrityError(SecurityError):
    """Raised when an audit chain fails verification."""


class StorageKeyError(SecurityError):
    """Raised when the encryption key is missing or invalid."""
