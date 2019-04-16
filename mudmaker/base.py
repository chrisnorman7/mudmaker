"""Provides the BaseObject class."""

from attr import attrs, attrib, Factory

NoneType = type(None)


@attrs
class BaseObject:
    """Contains id, name and description attributes."""

    name = attrib()
    description = attrib(default=Factory(NoneType))
    id = attrib(default=Factory(NoneType), init=False)
    game = attrib(default=Factory(NoneType))

    def get_description(self):
        return self.description or 'You see nothing special.'
