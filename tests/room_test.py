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


def test_link(room, game):
    direction = game.directions['n']
    destination = game.make_object('Room', (Room,), name='Other side')
    x = room.link(destination, direction)
    assert x.direction is direction
    assert x.name is None
    assert x.location is room
    assert x.destination is destination
