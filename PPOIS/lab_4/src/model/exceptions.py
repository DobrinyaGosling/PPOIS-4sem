class DomainError(Exception):
    """Base error for domain-level failures."""


class ValidationError(DomainError):
    """Invalid user input or invalid object state."""


class NotFoundError(DomainError):
    """Requested entity is missing."""
