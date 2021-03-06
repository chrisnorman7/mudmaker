"""Provides the Room class."""

from .attributes import Attribute, object
from .base import BaseObject
from .exits import Exit


class Room(BaseObject):
    """A room which contains objects."""

    zone = Attribute(None, 'The zone this room is part of', type=object)
    x = Attribute(0, 'X coordinate', type=int)
    y = Attribute(0, 'Y coordinate', type=int)
    z = Attribute(0, 'Z coordinate', type=int)

    def message_all(self, text):
        """Send a message text to everyone else in this room."""
        for obj in self.contents:
            obj.message(text)

    def message_all_but(self, objects, text):
        """Message everyone in this room with text, apart from those in the
        objects list."""
        for obj in self.contents:
            if obj not in objects:
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

    @property
    def coordinates(self):
        return (self.x, self.y, self.z)

    @coordinates.setter
    def coordinates(self, coords):
        (self.x, self.y, self.z) = coords

    @classmethod
    def on_init(cls, instance):
        """Add this room to self.game.rooms."""
        instance.game.rooms[instance.id] = instance
        instance.parser = None

    @classmethod
    def on_delete(cls, instance):
        del instance.game.rooms[instance.id]

    def match_exit(self, direction):
        """Return an exit in the given direction, or None if there is no
        match."""
        exits = [x for x in self.exits if x.direction is direction]
        if exits:
            return exits[0]

    def link(self, other, direction, name=None):
        """Link this room to other via the given direction. Also add an
        optional name."""
        return self.game.make_object(
            'Exit', (Exit,), direction_name=direction.name, location=self,
            destination=other, name=name
        )
