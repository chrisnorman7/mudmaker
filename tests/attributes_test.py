from mudmaker import Attribute, text


def test_init():
    value = 'Test name'
    description = 'Test description'
    a = Attribute(value, description)
    assert a.value == value
    assert a.description == description
    assert a.save is True
    assert a.visible is True
    assert a.type is str


def test_type():
    a = Attribute(None, 'This is a description', type=text)
    assert a.type is text
