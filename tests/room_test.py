from mudmaker import Room


def test_init(game, room):
    assert isinstance(room, Room)
    room.game = game
    assert room.contents == []
