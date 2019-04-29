from mudmaker import Exit, Room


def test_init(game, exit):
    assert isinstance(exit, Exit)
    assert isinstance(exit.location, Room)
    assert isinstance(exit.destination, Room)
    assert exit.game.exits[exit.id] is exit
    assert game._objects[exit.id] is exit
    assert exit.direction is game.directions['n']
    assert exit.state is exit.NOT_DOOR


def test_other_side(exit):
    os = exit.game.make_object(
        'Exit', (Exit,), location=exit.destination, destination=exit.location,
        name='Other Side'
    )
    assert exit.other_side is os
    assert os.other_side is exit


def test_exits(exit):
    r = exit.location
    d = exit.destination
    assert exit in r.exits
    assert exit in d.entrances


def test_delete(game, exit):
    exit.delete()
    assert exit.id not in game.exits
    assert exit.id not in game._objects


def test_direction(exit, game):
    d = game.directions['s']
    exit.direction = d
    assert exit.direction is d
    assert exit.direction_name == d.name


def test_name(game):
    d = game.directions['n']
    x = game.make_object('Exit', (Exit,), direction_name=d.name)
    assert x.name is None
    assert x.get_name() == d.name
    x.name = 'test'
    assert x.get_name() == x.name


def test_lock(exit, obj):
    exit.lock(obj)
    assert exit.state is exit.LOCKED


def test_unlock(exit, obj):
    exit.unlock(obj)
    assert exit.state is exit.CLOSED


def test_open(exit, obj):
    exit.open(obj)
    assert exit.state is exit.OPEN


def test_close(exit, obj):
    exit.close(obj)
    assert exit.state is exit.CLOSED
