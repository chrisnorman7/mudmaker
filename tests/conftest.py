from pytest import fixture

from mudmaker import Game, Room, Zone


@fixture(name='game')
def get_game():
    """Get a Game instance."""
    return Game()


@fixture(name='room')
def get_room():
    return Room('Test Room')


@fixture(name='zone')
def get_zone():
    return Zone('Test Zone')
