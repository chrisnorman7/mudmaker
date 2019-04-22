"""Provides the Object class."""

from .base import BaseObject, LocationMixin
from .exc import NoSuchObjectError


class Object(BaseObject, LocationMixin):
    """An object in the database."""

    @classmethod
    def on_init(cls, instance):
        """Add this object to self.game.objects."""
        instance.game.objects[instance.id] = instance

    @property
    def account(self):
        """Get any account object associated with this object."""
        try:
            return self.game.account_store.account_for(self)
        except NoSuchObjectError:
            pass  # return None.
