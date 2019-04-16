"""Provides the Zone class."""

from attr import attrs

from .base import BaseObject


@attrs
class Zone(BaseObject):
    """A zone with a list of rooms."""

    def add_room(self, room):
        """Add a Room object to this zone."""
        room.zone = self

    @property
    def rooms(self):
        """Get a list of rooms contained in this zone."""
        return [r for r in self.game.rooms.values() if r.zone is self]
