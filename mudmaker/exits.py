"""Provides the Exit class."""

from .attributes import Attribute, object
from .base import BaseObject, LocationMixin


class Exit(BaseObject, LocationMixin):
    """Link two rooms together."""

    destination = Attribute(
        None, 'The other side of this exit', type=object, visible=False
    )

    @property
    def other_side(self):
        exits = [x for x in self.game.exits if x.location is self.destination
                 and x.destination is self.location]
        return exits[0]
