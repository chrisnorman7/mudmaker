"""Provides the Object class."""

from .base import BaseObject, LocationMixin


class Object(BaseObject, LocationMixin):
    """An object in the database."""

    @classmethod
    def on_init(cls, instance):
        """Add this object to self.game.objects."""
        instance.game.objects[instance.id] = instance
