from mudmaker import Direction


def test_directions(game):
    d = game.directions['north']
    assert isinstance(d, Direction)
    assert d.x == 0
    assert d.y == 1
    assert d.z == 0
    assert game.directions['n'] is d
    assert d.game is game


def test_coordinates_from(game):
    d = game.directions['n']
    assert d.coordinates_from([0, 0, 0]) == (0, 1, 0)
    assert d.coordinates_from([5, 6, 7]) == (5, 7, 7)


def test_opposite(game):
    d = game.directions['n']
    o = d.opposite
    assert o.name == 'south'
    assert game.directions['s'] is o
