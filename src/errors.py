class ATSAPIError(Exception):
    """Base exception for ATS API errors."""

    def __init__(
        self,
        message: str,
        error_code: str = "ATS_API_ERROR",
    ):
        self.message = message
        self.error_code = error_code
        super().__init__(message)


class JobNotFoundError(ATSAPIError):
    """Raised when an asynchronous job does not exist."""

    def __init__(self, job_id: str):
        super().__init__(
            message=f"Job '{job_id}' was not found.",
            error_code="JOB_NOT_FOUND",
        )


class InvalidResumeError(ATSAPIError):
    """Raised when an uploaded resume is invalid."""

    def __init__(self, message: str = "Invalid resume file."):
        super().__init__(
            message=message,
            error_code="INVALID_RESUME",
        )
        