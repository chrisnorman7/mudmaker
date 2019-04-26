"""Provides the Zone class."""

from .base import BaseObject


class Zone(BaseObject):
    """A zone with a list of rooms."""

    def add_room(self, room):
        """Add a Room object to this zone."""
        room.zone = self

    @property
    def rooms(self):
        """Get a list of rooms contained in this zone."""
        return [r for r in self.game.rooms.values() if r.zone is self]

    @classmethod
    def on_init(cls, instance):
        """Add this zone to self.game.zones."""
        instance.game.zones[instance.id] = instance

    @classmethod
    def on_delete(cls, instance):
        del instance.game.zones[instance.id]
