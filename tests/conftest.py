from pytest import fixture

import os
import os.path

from autobahn.twisted import WebSocketServerFactory

from mudmaker import Exit, Game, Room, Zone, WebSocketConnection, Object


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


class PretendPeer:
    host = 'test.example.com'
    port = 1234


class PretendReason:
    def getErrorMessage(self):
        return 'Test conection was disconnected.'


class PretendTransport:
    def setTcpNoDelay(self, value):
        pass

    def getPeer(self):
        return PretendPeer()


class PretendConnection(WebSocketConnection):
    """A pretend connection."""

    def __init__(self, *args, **kwargs):
        self.transport = PretendTransport()
        super().__init__(*args, **kwargs)
        self.messages = []

    @property
    def last_message(self):
        if self.messages:
            return self.messages[-1]
        return ''

    def send(self, *args, **kwargs):
        pass

    def message(self, string):
        self.messages.append(string)
        return super().message(string)


@fixture(name='connection')
def connection(game):
    """Provides a pretend conection object."""
    game.websocket_factory = WebSocketServerFactory()
    game.websocket_factory.game = game
    con = PretendConnection()
    con.factory = game.websocket_factory
    con.onOpen()
    return con


@fixture(name='obj')
def get_object(game):
    return game.make_object('Object', (Object,), name='Test Object')


@fixture(name='accounts')
def get_accounts(game):
    """Get an AccountStore instance."""
    return game.account_store


@fixture(name='yaml_filename', scope='session', autouse=True)
def get_filename():
    # Will be executed before the first test
    filename = 'test.yaml'
    yield filename
    os.remove(filename)


@fixture(name='player')
def get_player(connection, game, accounts, obj):
    accounts.add_account('test', 'test', obj)
    game.finish_login(connection, obj)
    return obj
