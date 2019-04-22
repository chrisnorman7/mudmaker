from mudmaker import Object


def test_init(game, obj):
    assert isinstance(obj, Object)
    assert game.objects[obj.id] is obj


def test_account_for(obj, accounts):
    assert obj.account is None
    a = accounts.add_account('test', 'test', obj)
    assert obj.account is a
