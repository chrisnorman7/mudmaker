from mudmaker import Object


def test_init(game, obj):
    assert isinstance(obj, Object)
    assert obj.parser is None
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


def test_look_here(player, accounts, room):
    con = player.connection
    player.location = room
    player.look_here()
    name = '[%s; %s]' % (room.zone.name, room.name)
    assert con.messages[-2] == name
    assert con.messages[-1] == room.get_description()


def test_copy(obj, game, room):
    obj.location = room
    copy = obj.copy()
    assert copy.name == obj.name
    assert copy.description == obj.description
    assert copy.location is None
    assert copy.id != obj.id
    assert game.objects[copy.id] is copy
