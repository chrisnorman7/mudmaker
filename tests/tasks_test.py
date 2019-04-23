from functools import partial

from pytest import raises
from twisted.internet.defer import Deferred
from twisted.internet.task import LoopingCall

from mudmaker import Task
from mudmaker.exc import InvalidArgumentError


def test_init(game):

    @game.task(15)
    def t():
        pass

    assert isinstance(t, Task)
    assert isinstance(t.func, partial)
    assert isinstance(t.loop, LoopingCall)
    assert isinstance(t.deferred, Deferred)


def test_invalid_argument(game):
    with raises(InvalidArgumentError) as exc:
        game.task(15)(lambda text: print(text))
    name, ctx = exc.value.args
    assert name == 'text'
    assert isinstance(ctx, dict)


def test_start(game):

    @game.task(15)
    def t(task):
        task.works = True

    assert t.works is True
