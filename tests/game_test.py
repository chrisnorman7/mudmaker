from mudmaker import Game, Zone

from attr import attrs, attrib, Factory


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
