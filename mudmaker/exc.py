"""Provides various Exception-derived classes."""


class MudMakerError(Exception):
    """All errors will derive from this class."""


class ObjectError(MudMakerError):
    """There was an error with an object."""


class ExtraKwargsError(ObjectError):
    """Extra keyword arguments were passed to a class's __init__ method."""
