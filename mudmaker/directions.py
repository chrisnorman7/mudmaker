"""Provides the Direction class."""

from attr import attrs, attrib


@attrs
class Direction:
    """A direction to be used with an exit."""

    game = attrib()
    name = attrib()
    x = attrib()
    y = attrib()
    z = attrib()

    def coordinates_from(self, start):
        """Apply this direction to coordinates start and return the
        destination coordinates."""
        x, y, z = start
        return (
            x + self.x,
            y + self.y,
            z + self.z
        )

    @property
    def opposite(self):
        """Get the opposite direction."""
        x = self.x * -1
        y = self.y * -1
        z = self.z * -1
        directions = [
            d for d in self.game.directions.values() if d.x == x and
            d.y == y and d.z == z
        ]
        if directions:
            return directions[0]
