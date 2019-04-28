from mudmaker import Object
from mudmaker.base import EventBase


class PretendBase(EventBase):
    @classmethod
    def on_delete(cls, instance):
        instance.game.deleted = True


def test_init(game, obj):
    assert isinstance(obj, Object)
    assert obj.parser is None
    assert game.objects[obj.id] is obj
    assert obj.following is None
    assert obj.followers == []


def test_account_for(obj, accounts):
    assert obj.account is None
    a = accounts.add_account('test', 'test', obj)
    assert obj.account is a


def test_attributes(obj):
    assert len(obj.attributes)


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


def test_delete(game):
    o = game.make_object('Object', (Object, PretendBase))
    assert game._objects[o.id] is o
    o.delete()
    assert game.deleted is True
    assert o.id not in game._objects


def test_delete_account(obj, game, accounts):
    a = accounts.add_account('test', 'test123', obj)
    obj.delete()
    assert a.username not in accounts.accounts
    assert obj.id not in accounts.objects


def test_followers(game, obj, room):
    other = game.make_object(
        'Object', (Object,), name='The other object', location=room
    )
    obj.location = room
    obj.following = other
    assert obj.followers == []
    assert other.followers == [obj]


def test_follow(player, connection, room, game):
    player.location = room
    other = game.make_object(
        'Object', (Object,), name='Other Object', location=room
    )
    other.follow(player)
    assert other.following is player
    assert player.followers == [other]
    expected = f'{other.get_name()} starts following you.'
    assert connection.last_message == expected


def test_clear_following(player, game, connection, room):
    player.location = room
    other = game.make_object(
        'Object', (Object,), name='Other Object', location=room
    )
    other.follow(player)
    other.clear_following()
    assert other.following is None
    assert player.followers == []
    expected = f'{other.get_name()} stops following you.'
    assert connection.last_message == expected


def test_get_name(obj):
    assert obj.get_name() == obj.name


def test___str__(obj):
    assert str(obj) == obj.get_full_name()


def test_full_name(obj):
    expected = f'{obj.get_name()} (#{obj.id})'
    assert obj.get_full_name() == expected
