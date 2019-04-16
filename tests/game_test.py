from mudmaker import Game


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
