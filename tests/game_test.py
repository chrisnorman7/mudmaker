from attr import attrs, attrib, Factory
from pytest import raises
from yaml import dump

from mudmaker import Game, Zone
from mudmaker.game import ObjectValue


def test_init(game):
    assert isinstance(game, Game)
    assert game.rooms == {}
    assert game.objects == {}
    assert game.zones == {}
    assert game.connections == []


def test_new_id(game):
    assert game.max_id == 0
    assert game.new_id() == 1
    assert game.max_id == 1


def test_register_base(game):
    name = 'test'
    value = 12345

    @game.register_base(name)
    @attrs
    class PretendBase:
        number = attrib(default=Factory(lambda: value))

    assert game.bases[name] is PretendBase


def test_make_object(game):
    name = 'Test Zone'
    z = game.make_object(Zone.__name__, (Zone,), name=name)
    assert Zone in type(z).__bases__
    assert z.name == name
    assert z.game is game
    assert z.id == game.max_id


def test_players(game, obj, accounts):
    assert game.players == []
    accounts.add_account('username', 'password', obj)
    assert game.players == [obj]
    accounts.remove_account(obj)
    assert game.players == []


def test_as_dict(game, obj):
    assert game.as_dict() == dict(objects=[obj.dump()])


def test_dump(game, obj, room, yaml_filename):
    obj.location = room
    game.filename = yaml_filename
    yaml = dump(game.as_dict())
    game.dump()
    with open(game.filename, 'r') as f:
        assert yaml == f.read()


def test_from_dict(game, obj, room):
    obj.location = room
    with raises(RuntimeError):
        game.from_dict(game.as_dict())
    g = Game('Second Test Game')
    g.from_dict(game.as_dict())
    assert g.as_dict() == game.as_dict()


def test_load(game, obj, room, yaml_filename):
    obj.location = room
    game.filename = yaml_filename
    g = Game('Second Test Game', filename=game.filename)
    d = game.as_dict()
    game.dump()
    g.load()
    assert g.as_dict() == d


def test_dump_value(game, obj):
    assert game.dump_value('test') == 'test'
    assert game.dump_value(
        dict(location=obj)
    ) == dict(location=ObjectValue(obj.id))
    assert game.dump_value(
        [obj, obj]
    ) == [ObjectValue(obj.id), ObjectValue(obj.id)]
    assert game.dump_value(
        dict(objects=[obj, obj])
    ) == dict(objects=[ObjectValue(obj.id), ObjectValue(obj.id)])


def test_load_value(game, obj):
    assert game.load_value('test') == 'test'
    assert game.load_value(
        dict(location=ObjectValue(obj.id))
    ) == dict(location=obj)
    assert game.load_value(
        [ObjectValue(obj.id), ObjectValue(obj.id)]
    ) == [obj, obj]
    assert game.load_value(
        dict(objects=[ObjectValue(obj.id), ObjectValue(obj.id)])
    ) == dict(objects=[obj, obj])
