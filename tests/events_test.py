from pytest import raises

from mudmaker.base import BaseObject, EventBase


class Works(Exception):
    pass


class PretendBase(EventBase):

    @classmethod
    def on_init(cls, instance):
        raise Works()


class OnDumpBase(EventBase):
    @classmethod
    def on_dump(cls, instance, data):
        data['called'] = True


def test_on_init(game):
    with raises(Works):
        game.make_object('TestObject', (BaseObject, PretendBase))


def test_on_dump(game):
    obj = game.make_object('Object', (BaseObject, OnDumpBase))
    d = obj.dump()
    assert d['called'] is True
