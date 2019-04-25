from mudmaker.parsers import main_parser
from mudmaker.socials import Social


def test_socials_factory(game, socials):
    assert game.socials_factory is socials


def test_name(obj, socials):
    assert socials.suffixes['name'](obj, 'n') == ('you', obj.name)


def test_ss(obj, socials):
    assert socials.suffixes['ss'](obj, 'ss') == ('your', f"{obj.name}'s")


def test_social():
    name = 'test'
    first = '%1N test%1s.'
    second = '%1N test%1s something.'
    third = '%1N test%1s %2n.'
    description = 'Test something.'
    s = main_parser.social(name, first, second, third, description=description)
    assert isinstance(s, Social)
    for cmd in main_parser.commands:
        if cmd.name == name:
            f = cmd.func
            assert f.func is s
            assert f.args == ['player', 'target']
            break
    else:
        raise RuntimeError('Command not found.')
    assert s.no_target == first
    assert s.self_target == second
    assert s.any_target == third
    assert s.__doc__ == description
