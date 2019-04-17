from pytest import fixture

from mudmaker import Game, Room, Zone


@fixture(name='game')
def get_game():
    """Get a Game instance."""
    return Game()


@fixture(name='room')
def get_room(game):
    return game.make_object('Room', (Room,), name='Test Room')


@fixture(name='zone')
def get_zone(game):
    return game.make_object('Zone', (Zone,), name='Test Zone')
