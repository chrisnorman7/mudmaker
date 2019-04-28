from mudmaker import Room, Exit


def test_init(game, room):
    assert isinstance(room, Room)
    assert room.game is game
    assert room.contents == []
    assert room.parser is None
    assert game.rooms[room.id] is room
    assert game._objects[room.id] is room


def test_delete(room, game):
    room.delete()
    assert room.id not in game.rooms


def test_match_exit(room, game):
    d = game.directions['s']
    assert room.match_exit(d) is None
    x = game.make_object('Exit', (Exit,), direction_name=d.name, location=room)
    assert room.match_exit(d) is x
