from pytest import raises

from mudmaker.base import BaseObject, EventBase


class Works(Exception):
    pass


class PretendBase(EventBase):

    @classmethod
    def on_init(cls, instance):
        raise Works()


def test_on_init(game):
    with raises(Works):
        game.make_object('TestObject', (BaseObject, PretendBase))
