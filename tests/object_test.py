from mudmaker import Object


def test_init(game, obj):
    assert isinstance(obj, Object)
    assert game.objects[obj.id] is obj


def test_account_for(obj, accounts):
    assert obj.account is None
    a = accounts.add_account('test', 'test', obj)
    assert obj.account is a


def test_attributes(obj):
    assert obj.attributes == ['description', 'id', 'location', 'name']


def test_dump(obj):
    attributes = dict(id=1, name='Test Object')
    d = dict(class_name='Object', bases=['Object'], attributes=attributes)
    assert obj.dump() == d
    description = 'Test Description'
    obj.description = description
    assert obj.dump() != d
    attributes['description'] = description
    assert obj.dump() == d
