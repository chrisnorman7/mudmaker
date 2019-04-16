from mudmaker import Game

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
