"""Business logic, independent of HTTP."""


class ValidationError(Exception):
    """Raised when user input is invalid; the message is safe to show."""
