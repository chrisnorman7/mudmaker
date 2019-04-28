"""Provides the Exit class."""

from .attributes import Attribute, object
from .base import BaseObject, LocationMixin


class Exit(BaseObject, LocationMixin):
    """Link two rooms together."""

    destination = Attribute(
        None, 'The other side of this exit', type=object, visible=False
    )
    direction_name = Attribute(
        None, 'The name of the direction this exit faces'
    )

    @property
    def other_side(self):
        exits = [x for x in self.game.exits.values() if x.location is
                 self.destination and x.destination is self.location]
        if exits:
            return exits[0]

    @property
    def direction(self):
        return self.game.directions[self.direction_name]

    @direction.setter
    def direction(self, value):
        self.direction_name = value.name

    @classmethod
    def on_init(cls, instance):
        """Add this exit to self.game.exits."""
        instance.game.exits[instance.id] = instance

    @classmethod
    def on_delete(cls, instance):
        del instance.game.exits[instance.id]
