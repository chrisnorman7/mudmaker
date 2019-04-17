from mudmaker import Exit, Room


def test_init(game, exit):
    assert isinstance(exit, Exit)
    assert isinstance(exit.location, Room)
    assert isinstance(exit.destination, Room)
    assert exit.game.exits[exit.id] is exit
    assert game._objects[exit.id] is exit


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
