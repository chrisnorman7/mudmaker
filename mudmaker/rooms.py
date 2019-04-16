"""Provides the Room class."""

from attr import attrs, attrib, Factory

from .base import BaseObject


@attrs
class Room(BaseObject):
    """A room which contains objects."""

    zone = attrib(default=Factory(type(None)))
    exits = attrib(default=Factory(list))

    def broadcast(self, text):
        """Send a message text to everyone else in this room."""
        for obj in self.contents:
            obj.message(text)

    @property
    def contents(self):
        return [o for o in self.game.objects.values() if o.location is self]
