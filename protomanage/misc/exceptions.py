"""TODO docs: write docstring"""

class ChildClassError(Exception):
    """Base exception for child class implementation errors."""

class ChildClassMetadataError(ChildClassError):
    """Exception raised when a child class does not override required from its base class."""
