from mudmaker.base import BaseObject


def test_base_object():
    name = 'This is a name'
    o = BaseObject(name)
    assert o.id is None
    assert o.name == name
    assert o.description is None


def test_get_description():
    description = 'This is a description.'
    o = BaseObject('Name')
    assert o.get_description() == 'You see nothing special.'
    o.description = description
    assert o.get_description() == description
