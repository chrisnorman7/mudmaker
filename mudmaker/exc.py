"""Provides various Exception-derived classes."""


class MudMakerError(Exception):
    """All errors will derive from this class."""


class ObjectError(MudMakerError):
    """There was an error with an object."""


class ExtraKwargsError(ObjectError):
    """Extra keyword arguments were passed to a class's __init__ method."""


class CommandError(MudMakerError):
    """There was a problem with a command."""


class DontSaveCommand(CommandError):
    """Don't save this command to the connection."""


class AccountError(MudMakerError):
    """An error in the accounts system."""


class DuplicateUsernameError(AccountError):
    """There is already an account with that username."""


class DuplicateObjectError(AccountError):
    """There is already an account bound to that object."""


class NoSuchObjectError(AccountError):
    """There is no account associated with that object."""


class AuthenticationError(MudMakerError):
    """There was an error with authentication."""


class InvalidUsernameError(AuthenticationError):
    """An invalid username was entered."""


class InvalidPasswordError(AuthenticationError):
    """An invalid password was entered."""
