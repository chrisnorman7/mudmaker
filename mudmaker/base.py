"""Provides the BaseObject class."""

from .attributes import Attribute, text
from .exc import ExtraKwargsError


class EventBase:
    """A class which provides the most common events for database objects. All
    events should be decorated with @classmethod."""

    @classmethod
    def on_init(cls, instance):
        """Called when the object is initialised."""
        pass

    @classmethod
    def on_dump(cls, instance, dump):
        """Called as part of this object's .dump method. The dump argument is
        the dictionary of dumped data."""
        pass

    @classmethod
    def on_delete(cls, instance):
        """Called when this object is deleted."""
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

    def __repr__(self):
        string = f'{type(self).__name__}('
        attributes = (
            (name, repr(getattr(self, name))) for name in self.attributes
        )
        string += ', '.join('='.join(thing) for thing in attributes)
        return string + ')'

    def delete(self):
        """Delete this object."""
        del self.game._objects[self.id]
        for base in type(self).__bases__:
            base.on_delete(self)

    def get_description(self):
        return self.description or 'You see nothing special.'

    def __str__(self):
        """Return a pretty string representing this object."""
        return '%s (#%s)' % (self.name, self.id)

    @property
    def attributes(self):
        """Return a list of Attribute instances for this object's class."""
        cls = type(self)
        return [x for x in dir(cls) if isinstance(getattr(cls, x), Attribute)]

    def dump(self):
        """Return this object as a dictionary, for use with Game.dump."""
        cls = type(self)
        d = dict(class_name=cls.__name__)
        d['bases'] = [b.__name__ for b in cls.__bases__]
        attributes = {}
        for name in self.attributes:
            attribute = getattr(cls, name)
            value = getattr(self, name)
            if not attribute.save or value == attribute.value:
                continue
            # The attribute should be saved, and is different from the default.
            attributes[name] = value
        d['attributes'] = attributes
        cls.on_dump(self, d)
        return d

    def get_full_name(self):
        """Get the name (including ID) of this object."""
        return '%s (#%s)' % (self.name, self.id)

    def copy(self):
        """Return a copy of this object. All editable attributes will be
        identical to those set on this object. All non-editable attributes - id
        for example - will revert to their defaults."""
        cls = type(self)
        kwargs = {
            name: getattr(self, name) for name in self.attributes if getattr(
                cls, name
            ).visible
        }
        return self.game.make_object(cls.__name__, cls.__bases__, **kwargs)


class LocationMixin:
    """Add location information."""

    location = Attribute(
        None, 'The location of this object', type=object, visible=False
    )
