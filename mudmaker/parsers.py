"""Provides the two main command parsers: login_parser, and main_parser."""

from datetime import datetime
from functools import partial

from commandlet import Parser, command
from .exc import AuthenticationError
from .objects import Object
from .util import get_login, english_list


class MudMakerParser(Parser):
    """A parser with extra socials."""

    def social(self, social):
        """Add a social to this parser."""
        name = social.name
        p = partial(social.use_nothing)
        p.__doc__ = name + '.'
        self.command(name)(p)
        p = partial(social.use_target)
        p.__doc__ = social.description
        self.command(f'{name} <object:target>')(p)


login_parser = Parser()


@login_parser.command('create', 'new', 'create <username> <password>')
def do_create(con, accounts, game, username=None, password=None):
    """Create a new character."""
    if not username:
        prompt = con.prompt_text
        username, password = yield from get_login(con)
        con.set_prompt_text(prompt)
    while True:
        con.message('Enter a name for your new character (or quit to exit):')
        name = yield
        if name == 'quit':
            return
        elif not name:
            con.message('Names must not be blank.')
        elif list(
            filter(
                lambda obj: obj.name.lower().startswith(name),
                game.objects.values()
            )
        ):
            con.message(
                'There is already a player with that name. Please choose '
                'another.'
            )
        else:
            break
    if accounts.account_exists(username):
        con.message(
            'There is already an account with that username. Please pick '
            'another.'
        )
        return
    player = game.make_object('Object', (Object,), name=name)
    if not game.players:
        kwargs = dict(builder=True, admin=True)
        con.message(
            'You are the first connected player. You have been made an '
            'administrator.'
        )
    else:
        kwargs = {}
    accounts.add_account(username, password, player, **kwargs)
    con.message('You have successfully created a new character.')
    game.finish_login(con, player)


main_parser = MudMakerParser()


@main_parser.filter('object')
def object_filter(player, text):
    """Attempt to return a match."""
    return player.single_match(text)


@command([login_parser, main_parser], 'host', '@host', '@hostname')
def do_hostname(con, host):
    """Get your host name and port."""
    con.message('You are connected from %s.' % host)


@command([login_parser, main_parser], 'help', 'help', '@commands', r'\?')
def do_help(con, parser):
    """Get a list of possible commands."""
    con.message('Commands available to you:')
    commands = {}
    for cmd in sorted(parser.commands, key=lambda cmd: cmd.name):
        if cmd.name not in commands:
            commands[cmd.name] = [
                cmd.func.func.__doc__ or 'No description available.'
            ]
        commands[cmd.name].append(cmd.usage)
    for name, values in commands.items():
        con.message('%s:' % name)
        formats = [x.replace('\\', '') for x in values[1:]]
        con.message(', '.join(formats) + '.')
        con.message(values[0])


@command([login_parser, main_parser], 'uptime', '@uptime')
def do_uptime(game, con):
    """Show server uptime."""
    now = datetime.utcnow()
    con.message('Uptime: %s.' % (now - game.started))
    con.message('Server started: %s.' % now.ctime())


@command([login_parser, main_parser], 'quit', 'quit', '@quit')
def do_quit(con):
    """Quit the game."""
    con.disconnect('Goodbye.')


@login_parser.command('login', 'connect <username> <password>', '<username>')
def do_login(game, con, username, password=None):
    """Log in a character."""
    prompt = con.prompt_text
    if not password:
        con.get_password('Password:')
        password = yield
    try:
        player = game.account_store.authenticate(username, password)
        game.finish_login(con, player)
    except AuthenticationError:
        con.logger.info('Attempted to login as %s.', username)
        con.message('Invalid username or password.')
        con.set_prompt_text(prompt)


@main_parser.command('look', 'look <object:thing>', 'l', 'l <object:thing>')
def look(player, location, thing=False):
    """Look around, or at something in this room."""
    if location is None:
        player.message('You cannot look here.')
    elif thing is not False:
        if thing is not None:
            player.message(thing.name)
            player.message(thing.get_description())
    else:
        player.look_here()


@main_parser.command('say', 'say <string>', '"<string>', "'<string>")
def do_say(player, string):
    """Say something."""
    player.do_say(string)


@main_parser.command('socials', '@socials', '@socials <social>')
def do_socials(player, game, socials, social=None):
    """Show a list of socials, or show what a certain social will do."""
    if social is None:
        player.message('Socials: %s.' % english_list(sorted(game.socials)))
    elif social in game.socials:
        social = game.socials[social]
        player.message(social.name)
        player.message(social.get_description())
        player.message('Social strings:')
        player.message('When used with no target:')
        player.message(social.no_target)
        player.message('When used on yourself:')
        player.message(social.self_target)
        player.message('When used with any other target:')
        player.message(social.any_target)
    else:
        player.message('There is no social by that name.')
