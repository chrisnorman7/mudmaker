from functools import partial

from mudmaker.parsers import main_parser
from mudmaker.socials import Social


def test_socials_factory(game, socials):
    assert game.socials_factory is socials


def test_name(obj, socials):
    assert socials.suffixes['name'](obj, 'n') == ('you', obj.name)


def test_ss(obj, socials):
    assert socials.suffixes['ss'](obj, 'ss') == ('your', f"{obj.name}'s")


def test_social(game, socials):
    name = 'test'
    first = '%1N test%1s.'
    second = '%1N test%1s thoroughly.'
    third = '%1N test%1s %2n.'
    s = game.make_object(
        'Social', (Social,), name=name, no_target=first, self_target=second,
        any_target=third
    )
    assert isinstance(s, Social)
    for cmd in main_parser.commands:
        if cmd.name == name:
            f = cmd.func
            p = f.func
            assert isinstance(p, partial)
            if cmd.usage == s.name:
                assert p.func == s.use_nothing
                assert f.args == ['player']
                assert p.__doc__ == f'{s.name}.'
            else:
                assert p.func == s.use_target
                assert f.args == ['player', 'target']
                assert p.__doc__ == f'{s.name} at someone or something.'
            break
    else:
        raise RuntimeError('Command not found.')
    assert s.no_target == first
    assert s.self_target == second
    assert s.any_target == third


def test_delete(game):
    s = game.make_object(
        'Social', (Social,), name='delete', no_target='%1N delete%1s.',
        self_target='%1N delete%1s furiously.', any_target='%1N delete%1s %2n.'
    )
    length = len(main_parser.commands)
    s.delete()
    assert s.name not in game.socials
    assert len(main_parser.commands) == (length - 2)
