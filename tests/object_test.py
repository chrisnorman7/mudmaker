from mudmaker import Object


def test_init(game, obj):
    assert isinstance(obj, Object)
    assert game.objects[obj.id] is obj
