from pytest import fixture

from mudmaker import Game, Room, Zone


@fixture(name='game')
def get_game():
    """Get a Game instance."""
    return Game()


@fixture(name='room')
def get_room(game):
    return Room(game, name='Test Room')


@fixture(name='zone')
def get_zone(game):
    return Zone(game, name='Test Zone')
