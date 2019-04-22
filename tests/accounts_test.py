"""Test the builtin accounts system."""

import os
import os.path
from json import dumps

from pytest import raises

from mudmaker import Account, AccountStore, Object
from mudmaker.exc import (
    DuplicateUsernameError, DuplicateObjectError, InvalidUsernameError,
    InvalidPasswordError, NoSuchObjectError
)


def test_init(accounts):
    assert isinstance(accounts, AccountStore)
    assert accounts.accounts == {}
    assert accounts.objects == {}
    assert accounts.account_class is Account


def test_add_account(obj, accounts):
    username = 'test'
    password = 'test123'
    a = accounts.add_account(username, password, obj)
    assert isinstance(a, Account)
    assert a.object is obj
    assert accounts.accounts[username] is a
    assert accounts.objects[obj.id] is a


def test_duplicate_username(game, obj, accounts):
    username = 'test'
    password = 'testing123'
    accounts.add_account(username, password, obj)
    with raises(DuplicateUsernameError) as exc:
        accounts.add_account(
            username, password, game.make_object(
                'Object', (Object,), name='Second Object'
            )
        )
    assert exc.value.args == (username,)


def test_duplicate_object(obj, accounts):
    password = 'testing123'
    accounts.add_account('test1', password, obj)
    with raises(DuplicateObjectError) as exc:
        accounts.add_account('test2', password, obj)
    assert exc.value.args == (obj,)


def test_remove_account(obj, accounts):
    accounts.add_account('username', 'password', obj)
    accounts.remove_account(obj)
    assert not accounts.accounts
    assert not accounts.objects


def test_authenticate(obj, accounts):
    username = 'test'
    password = 'testing123'
    accounts.add_account(username, password, obj)
    assert accounts.authenticate(username, password) is obj
    with raises(InvalidUsernameError):
        accounts.authenticate('invalid', 'invalid')
    with raises(InvalidPasswordError):
        accounts.authenticate(username, 'invalid')


def test_account_for(obj, accounts):
    with raises(NoSuchObjectError) as exc:
        accounts.account_for(obj)
    assert exc.value.args == (obj,)
    a = accounts.add_account('test', 'test123', obj)
    assert accounts.account_for(obj) is a


def test_as_list(obj, accounts):
    assert accounts.as_list() == []
    a = accounts.add_account('test', 'test123', obj)
    assert accounts.as_list() == [
        dict(username=a.username, password=a.password, object_id=obj.id)
    ]


def test_dump(obj, accounts):
    if os.path.isfile(accounts.filename):
        os.remove(accounts.filename)
    accounts.add_account('test', 'test123', obj)
    try:
        accounts.dump()
        assert os.path.isfile(accounts.filename)
        with open(accounts.filename, 'r') as f:
            text = f.read()
        assert text == dumps(accounts.as_list(), indent=4)
    finally:
        os.remove(accounts.filename)


def test_load(obj, accounts, game):
    accounts.add_account('test', 'test123', obj)
    try:
        accounts.dump()
        a = AccountStore(game)
        a.load()
        assert a.accounts == accounts.accounts
        assert a.objects == accounts.objects
    finally:
        os.remove(a.filename)


def test_loaded(accounts):
    assert accounts.loaded is False
    with raises(InvalidUsernameError):
        accounts.authenticate('test', 'test')
    assert accounts.loaded is True
