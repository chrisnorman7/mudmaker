from pytest import fixture

from mudmaker import Exit, Game, Room, Zone


@fixture(name='exit')
def get_exit(game, zone):
    """Get a new exit linking two rooms."""
    location = game.make_object(
        'Room', (Room,), name='Test Location', zone=zone
    )
    destination = game.make_object(
        'Room', (Room,), name='Test Destination', zone=zone
    )
    return game.make_object(
        'Exit', (Exit,), location=location, destination=destination,
        name='Test Exit'
    )


@fixture(name='game')
def get_game():
    """Get a Game instance."""
    return Game()


@fixture(name='room')
def get_room(game, zone):
    return game.make_object('Room', (Room,), name='Test Room', zone=zone)


@fixture(name='zone')
def get_zone(game):
    return game.make_object('Zone', (Zone,), name='Test Zone')
