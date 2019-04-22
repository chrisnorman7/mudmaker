"""Provides the two main command parsers: login_parser, and main_parser."""

from datetime import datetime

from commandlet import Parser, command

from .util import get_login


login_parser = Parser()


@login_parser.command('login')
def do_login(con):
    """Log in a character."""
    username, password = yield from get_login(con)
    con.message('Logging in as %s:%s.' % (username, password))


@login_parser.command('create')
def do_create(con):
    """Create a new character."""
    username, password = yield from get_login(con)
    con.message('Creating %s:%s.' % (username, password))


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


@command([login_parser, main_parser], 'uptime', 'uptime', '@uptime')
def do_uptime(game, con):
    """Show server uptime."""
    now = datetime.utcnow()
    con.message('Uptime: %s.' % (now - game.started))
    con.message('Server started: %s.' % now.ctime())


@command([login_parser, main_parser], 'quit', 'quit', '@quit')
def do_quit(con):
    """Quit the game."""
    con.disconnect('Goodbye.')


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
