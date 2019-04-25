from mudmaker import Room


def test_init(game, room):
    assert isinstance(room, Room)
    assert room.game is game
    assert room.contents == []
    assert room.parser is None
    assert game.rooms[room.id] is room
    assert game._objects[room.id] is room
