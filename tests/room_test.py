from mudmaker import Room


def test_init(game, room):
    assert isinstance(room, Room)
    assert room.game is game
    assert room.contents == []
    assert game.rooms[room.id] is room
