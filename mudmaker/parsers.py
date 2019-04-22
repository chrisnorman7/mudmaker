"""Provides the two main command parsers: login_parser, and main_parser."""

from datetime import datetime

from commandlet import Parser, command

from .exc import AuthenticationError
from .objects import Object
from .util import get_login


def finish_login(con, player):
    """Connection an Object instance player to the connection con."""
    old = player.connection
    player.connection = con
    con.object = player
    player.message('Welcome back, %s.' % player.name)
    con.parser = main_parser
    if old is not None:
        old.message('*** You have logged in from somewhere else.')
        old.object = None
        old.disconnect('Goodbye.')


login_parser = Parser()


@login_parser.command('create', 'new', 'create <username> <password>')
def do_create(con, accounts, game, username=None, password=None):
    """Create a new character."""
    if not username:
        username, password = yield from get_login(con)
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
    accounts.add_account(username, password, player)
    con.message('You have successfully created a new character.')
    finish_login(con, player)


main_parser = Parser()


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
    if not password:
        con.message('Password:')
        password = yield
    try:
        player = game.account_store.authenticate(username, password)
        finish_login(con, player)
    except AuthenticationError:
        con.logger.info('Attempted to login as %s.', username)
        con.message('Invalid username or password.')


@main_parser.command('look', 'look <thing>', 'l', 'l <thing>')
def look(player, location, thing=None):
    """Look around, or at something in this room."""
    if location is None:
        player.message('You cannot look here.')
    elif thing:
        res = player.object_match(thing)
        if res is not None:
            player.message(res.get_name())
            player.message(res.get_description())
    else:
        player.look_here()
