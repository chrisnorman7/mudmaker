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
        """Get a list of exits."""
        return [x for x in self.game.exits.values() if x.location is self]

    @property
    def entrances(self):
        """Get a list of entrances."""
        return [x for x in self.game.exits.values() if x.destination is self]

    @classmethod
    def on_init(cls, instance):
        """Add this room to self.game.rooms."""
        instance.game.rooms[instance.id] = instance
