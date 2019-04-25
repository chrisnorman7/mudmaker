def test_socials_factory(game, socials):
    assert game.socials_factory is socials


def test_name(obj, socials):
    assert socials.suffixes['name'](obj, 'n') == ('you', obj.name)


def test_ss(obj, socials):
    assert socials.suffixes['ss'](obj, 'ss') == ('your', f"{obj.name}'s")
