"""Provides the Direction class."""

from attr import attrs, attrib


@attrs
class Direction:
    """A direction to be used with an exit."""

    name = attrib()
    x = attrib()
    y = attrib()
    z = attrib()
