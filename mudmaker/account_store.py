"""Provides the AccountStore class."""

from json import dump, load

from attr import attrs, attrib, Factory
from passlib.hash import sha256_crypt

from .exc import (
    DuplicateUsernameError, DuplicateObjectError, InvalidUsernameError,
    NoSuchObjectError, InvalidPasswordError
)

crypt = sha256_crypt.using(rounds=10000)


@attrs
class Account:
    """An account in the default accounts system. You do not have to use this
    class, but it is recommended you use it as a parent for your own class if
    you decide to extend the default AccountStore class."""

    username = attrib()
    password = attrib()
    object_id = attrib()
    game = attrib(repr=False)

    def verify(self, password):
        """Return a boolean representing whether the supplied password matches
        the account's password."""
        return crypt.verify(password, self.password)

    @property
    def object(self):
        return self.game.objects[self.object_id]


@attrs
class AccountStore:
    """A generic account store. If you're going to use another storage system,
    you should implement the add_account, remove_account, and authenticate
    methods."""

    game = attrib(repr=False)
    account_class = attrib(default=Factory(lambda: Account))
    accounts = attrib(default=Factory(dict))
    objects = attrib(default=Factory(dict))
    filename = attrib(default=Factory(lambda: 'accounts.json'))
    last_dump = attrib(default=Factory(type(None)))

    def encrypt_password(self, password):
        """Returns an encrypted version of the password for use by
        self.add_account. The default implementation uses
        passlib.hash.sha256_crypt with 10000 rounds."""
        return crypt.hash(password)

    def add_account(self, username, password, obj):
        """Add a user to the accounts database.

        Once the account is created, the user will be able to log in with the
        supplied username and password, and be connected to the supplied Object
        instance obj.

        This method uses self.encrypt_password to encrypt the password.

        If an account already exists with the given username,
        DuplicateUsernameError should be raised with the username as the only
        argument.

        If there is already an account bound to obj, then DuplicateObjectError
        should be raised with obj as the only argument."""
        password = self.encrypt_password(password)
        object_id = obj.id
        if username in self.accounts:
            raise DuplicateUsernameError(username)
        elif object_id in self.objects:
            raise DuplicateObjectError(obj)
        return self._add_account(username, password, object_id)

    def _add_account(self, username, password, object_id):
        """Backend for adding accounts. Accepts already-encrypted passwords for
        use by both self.add_account, and self.load."""
        account = self.account_class(username, password, object_id, self.game)
        self.accounts[username] = account
        self.objects[object_id] = account
        return account

    def remove_account(self, obj):
        """Remove an account for an Object instance obj."""
        object_id = obj.id
        account = self.objects.pop(object_id)
        del self.accounts[account.username]

    def authenticate(self, username, password):
        """Given a username and password combination, return an Object instance
        with a matching account. If the username is invalid,
        InvalidUsernameError is raised. If the password is invalid,
        InvalidPasswordError will be raised."""
        if username not in self.accounts:
            raise InvalidUsernameError()
        account = self.accounts[username]
        if account.verify(password):
            return account.object
        raise InvalidPasswordError()

    def account_for(self, obj):
        """Return the account object associated with an Object instance obj."""
        try:
            return self.objects[obj.id]
        except KeyError:
            raise NoSuchObjectError(obj)

    def as_list(self):
        """Returns a list of dictionaries representing all the registered
        accounts. Used by self.dump."""
        return [
            dict(
                username=a.username, password=a.password, object_id=a.object_id
            ) for a in self.accounts.values()
        ]

    def dump(self):
        """Write all the registered accounts to self.filename."""
        with open(self.filename, 'w') as f:
            dump(self.as_list(), f, indent=4)

    def load(self):
        """Load registered accounts from self.filename. If there are already
        accounts loaded, RuntimeError will be raised."""
        if self.accounts:
            raise RuntimeError(
                'Attempting to load accounts into a non-empty account store.'
            )
        with open(self.filename, 'r') as f:
            data = load(f)
        for row in data:
            username = row['username']
            password = row['password']
            object_id = row['object_id']
            self._add_account(username, password, object_id)
