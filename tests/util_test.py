"""Test utility methods."""

from mudmaker.util import yes_or_no, pluralise


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
