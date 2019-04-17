"""Provides the Attribute class, as well as some type classes for use with the
Attribute class."""

from attr import attrs, attrib, Factory


@attrs
class Attribute:
    """An attribute for an object. Can be marked as not to be dumped with the
    object by setting the same flag to False, and not to be visible to players
    by setting the visible flag to False."""

    value = attrib()
    description = attrib()
    type = attrib(default=Factory(lambda: str))
    save = attrib(default=Factory(lambda: True))
    visible = attrib(default=Factory(lambda: True))


class text(str):
    """A string which supports new line characters."""


class object:
    """The type of the attribute's value is a game object."""
