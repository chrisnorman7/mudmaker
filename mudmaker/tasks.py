"""Provides the Task class."""

from functools import partial
from inspect import signature

from attr import attrs, attrib, Factory
from twisted.internet.task import LoopingCall

from .exc import InvalidArgumentError

NoneType = type(None)


@attrs
class Task:
    """A task. Uses twisted.internet.task.LoopingCall."""

    game = attrib()
    func = attrib()
    id = attrib(default=Factory(NoneType), init=False)
    loop = attrib(default=Factory(NoneType), init=False, repr=False)
    deferred = attrib(default=Factory(NoneType), init=False, repr=False)

    def __attrs_post_init__(self):
        self.id = self.game.new_id()
        args = []
        ctx = dict(game=self.game, task=self, id=self.id)
        for parameter in signature(self.func).parameters.values():
            try:
                args.append(ctx[parameter.name])
            except KeyError:
                if parameter.default is parameter.empty:
                    raise InvalidArgumentError(parameter.name, ctx)
        self.func = partial(self.func, *args)
        self.loop = LoopingCall(self.func)

    def start(self, *args, **kwargs):
        """Call self.loop.start with all arguments, and store the resulting
        Deferred in self.deferred."""
        self.deferred = self.loop.start(*args, **kwargs)
