from mudmaker import Direction


def test_directions(game):
    d = game.directions['north']
    assert isinstance(d, Direction)
    assert d.x == 0
    assert d.y == 1
    assert d.z == 0
    assert game.directions['n'] is d
