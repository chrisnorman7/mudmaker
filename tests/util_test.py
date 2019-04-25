"""Test utility methods."""

from pytest import raises
from mudmaker.util import yes_or_no, pluralise, get_login, broadcast


def test_yes_or_no():
    assert yes_or_no('y') is True
    assert yes_or_no('ye') is True
    assert yes_or_no('yes') is True
    assert yes_or_no('no') is False


def test_pluralise():
    assert pluralise(1, 'gold') == 'gold'
    assert pluralise(2, 'rabbit') == 'rabbits'
    assert pluralise(0, 'rabbit') == 'rabbits'
    assert pluralise(45, 'person', plural='people') == 'people'


def test_get_login(connection):
    username = 'test'
    password = 'test123'
    res = get_login(connection)
    next(res)
    assert connection.last_message == 'Username:'
    res.send(username)
    assert connection.last_message == 'Password:'
    with raises(StopIteration) as exc:
        res.send(password)
    assert exc.value.args[0] == (username, password)


def test_broadcast(player, game, connection):
    assert player.connection is connection
    assert connection.object is player
    assert game.connections == [connection]
    msg = 'testing.'
    broadcast(game.connections, msg)
    assert connection.last_message == msg
