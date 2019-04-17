from pytest import raises

from mudmaker.base import BaseObject
from mudmaker.exc import ExtraKwargsError


def test_base_object(game):
    o = BaseObject(game)
    assert o.id == game.max_id
    assert o.name is None
    assert o.description is None


def test_get_description(game):
    description = 'This is a description.'
    o = BaseObject(game)
    assert o.get_description() == 'You see nothing special.'
    o.description = description
    assert o.get_description() == description


def test_valid_kwargs(game):
    name = 'Test Name'
    description = 'This is a test description.'
    o = BaseObject(game, name=name, description=description)
    assert o.name == name
    assert o.description == description


def test_invalid_kwargs(game):
    kwargs = dict(name='Test Name', test='failed')
    with raises(ExtraKwargsError) as exc:
        BaseObject(game, **kwargs)
    kwargs.pop('name')
    cls, kw = exc.value.args
    assert cls is BaseObject
    assert kw == kwargs
