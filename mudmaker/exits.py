"""Provides the Exit class."""

from .attributes import Attribute, object
from .base import BaseObject, LocationMixin
from .socials import factory


class Exit(BaseObject, LocationMixin):
    """Link two rooms together."""

    destination = Attribute(
        None, 'The other side of this exit', type=object, visible=False
    )
    direction_name = Attribute(
        None, 'The name of the direction this exit faces'
    )
    NOT_DOOR = 0  # This exit cannot be opened, closed, or locked.
    OPEN = 1  # This exit is open.
    CLOSED = 2  # This exit is closed, but not locked.
    LOCKED = 3  # This exit is closed and locked.
    state = Attribute(NOT_DOOR, 'The state of this exit', visible=False)
    keys = Attribute(
        [], 'The list of keys that will lock and unlock this door',
        visible=False, type=list
    )
    leave_msg = Attribute(
        '%1N {} %2n.', 'The string which is used when an object leaves through'
        ' this exit'
    )
    arrive_msg = Attribute(
        '%1N arrive%1s from {}.', 'The string which is used when an object '
        'arrives from this exit'
    )
    leave_follow_msg = Attribute(
        '%1N leave%1s behind %2n.', 'The string which is used when an object '
        'follows another out through this exit'
    )
    arrive_follow_msg = Attribute(
        '%1N arrive%1s behind %2n.', 'The string which is used when an object '
        'follows another in through this exit'
    )
    closed_msg = Attribute(
        '%1N must open %2n first.', 'The string which is sent to an object '
        'when it tries to use this exit before opening it'
    )
    open_msg = Attribute(
        '%1N open%1s %2n.', 'The message which is used when an object opens '
        'this exit'
    )
    close_msg = Attribute(
        '%1N close%1s %2n.', 'The string which is used when an object closes '
        'this exit'
    )
    locked_msg = Attribute(
        '%1N must unlock %2n first.', 'The string which is sent to an object '
        'when it tries to open this exit without unlocking it first'
    )
    unlock_msg = Attribute(
        '%1N unlock%1s %2n.', 'The string which is used when an object unlocks'
        ' this exit'
    )
    lock_msg = Attribute(
        '%1N lock%1s %2n.', 'The string which is used when an object locks '
        'this exit'
    )

    def get_name(self, verbose=False):
        """Return a proper name for this object."""
        if self.name is None:
            return self.direction_name
        else:
            return self.name

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

    def use(self, obj):
        """Use this exit as the Object obj."""
        if self.state in (self.OPEN, self.NOT_DOOR):
            obj.clear_following()
            msg = self.leave_msg.format(obj.walk_style)
            obj.do_social(msg, _others=[self])
            other = self.other_side
            if other is None:
                msg = '%1N arrive%1s.'
            else:
                name = other.get_name()
                if name == 'down':
                    name = 'below'
                elif name == 'up':
                    name = 'above'
                elif 'and' not in name:
                    name = 'the ' + name
                msg = other.arrive_msg.format(name)
            string = factory.get_strings(msg, [obj])[-1]
            d = self.destination
            d.message_all(string)
            obj.location = d
            obj.look_here()
            for follower in obj.followers:
                strings = factory.get_strings(
                    other.arrive_follow_msg, [follower, obj]
                )
                obj.message(strings[1])
                d.message_all_but([obj], strings[-1])
            strings = []
            for follower in obj.followers:
                follower.location = d
                follower.look_here()
                strings.append(
                    factory.get_strings(
                        self.leave_follow_msg, [follower, obj]
                    )[-1]
                )
            for string in strings:
                self.location.message_all(string)
        elif self.state is self.LOCKED:
            obj.message(factory.get_strings(self.locked_msg, [obj, self])[0])
        elif self.state is self.CLOSED:
            obj.message(factory.get_strings(self.closed_msg, [obj, self])[0])
        else:
            raise RuntimeError('Unrecognised state: %r.' % self.state)

    def lock(self, obj):
        """Have Object obj lock this exit."""
        self.state = self.LOCKED
        obj.do_social(self.lock_msg, [self])

    def unlock(self, obj):
        """Have Object obj unlock this exit and leave it closed."""
        self.state = self.CLOSED
        obj.do_social(self.unlock_msg, [self])

    def open(self, obj):
        """Have Object obj open this exit and leave it closable."""
        self.state = self.OPEN
        obj.do_social(self.open_msg, [self])

    def close(self, obj):
        """Have Object obj close this exit and leave it closed."""
        self.state = self.CLOSED
        obj.do_social(self.close_msg, [self])
