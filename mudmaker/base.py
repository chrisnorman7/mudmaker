"""Provides the BaseObject class."""

from .attributes import Attribute, text
from .exc import ExtraKwargsError


class EventBase:
    """A class which provides the most common events for database objects. All
    events should be decorated with @classmethod."""

    @classmethod
    def on_init(cls, instance):
        """Override to do something when the object is initialised."""
        pass


class BaseObject(EventBase):
    """The base class from which all game objects must derive."""

    id = Attribute(None, 'The ID of this object', type=int, visible=False)
    name = Attribute(None, 'The name of this object')
    description = Attribute(None, 'The description of this object', type=text)

    def __init__(self, game, **kwargs):
        """Initialise with a game object. All other keyword arguments are set
        as attributes, assuming type(self) has the given attribute as an
        instance of Attribute."""
        self.game = game
        if 'id' not in kwargs:
            kwargs['id'] = game.new_id()
        cls = type(self)
        for name in dir(cls):
            attribute = getattr(cls, name)
            if not isinstance(attribute, Attribute):
                continue
            setattr(self, name, kwargs.pop(name, attribute.value))
        if kwargs:
            raise ExtraKwargsError(cls, kwargs)

    def get_description(self):
        return self.description or 'You see nothing special.'
