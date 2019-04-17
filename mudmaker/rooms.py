"""Provides the Room class."""

from .attributes import Attribute, object
from .base import BaseObject


class Room(BaseObject):
    """A room which contains objects."""

    zone = Attribute(None, 'The zone this room is part of', type=object)

    def broadcast(self, text):
        """Send a message text to everyone else in this room."""
        for obj in self.contents:
            obj.message(text)

    @property
    def contents(self):
        return [o for o in self.game.objects.values() if o.location is self]

    @property
    def exits(self):
        return [x for x in self.game.exits if x.location is self]
