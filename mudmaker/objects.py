"""Provides the Object class."""

from .base import BaseObject, LocationMixin
from .exc import NoSuchObjectError


class Object(BaseObject, LocationMixin):
    """An object in the database."""

    @classmethod
    def on_init(cls, instance):
        """Add this object to self.game.objects."""
        instance.game.objects[instance.id] = instance
        instance.connection = None

    @property
    def account(self):
        """Get any account object associated with this object."""
        try:
            return self.game.account_store.account_for(self)
        except NoSuchObjectError:
            pass  # return None.

    def message(self, text):
        """Send some text to this object's connection."""
        if self.connection is not None:
            self.connection.message(text)
            return True
        return False
