"""Provides the two main command parsers: login_parser, and main_parser."""

from commandlet import Parser

login_parser = Parser()


@login_parser.command('host', 'host', 'hostname')
def do_hostname(con, host):
    """Get your host name and port."""
    con.message('You are connected from %s.' % host)


@login_parser.command('help', 'help', 'commands', r'\?')
def do_help(con, parser):
    """Get a list of possible commands."""
    con.message('Commands available to you:')
    commands = {}
    for cmd in sorted(parser.commands, key=lambda cmd: cmd.name):
        if cmd.name not in commands:
            commands[cmd.name] = [cmd.func.func.__doc__]
        commands[cmd.name].append(cmd.usage)
    for name, values in commands.items():
        con.message('%s:' % name)
        formats = [x.replace('\\', '') for x in values[1:]]
        con.message(', '.join(formats) + '.')
        con.message(values[0])


@login_parser.command('login', 'login <username> <password>')
def do_login(con, username, password):
    """Log in a character."""
    con.message('Logging in as %s:%s.' % (username, password))


@login_parser.command('create', 'create <username> <password>')
def do_create(con, username, password):
    """Create a new character."""
    con.message('Creating %s:%s.' % (username, password))


main_parser = Parser()


def do_quit(con):
    """Quit the game."""
    con.disconnect('Goodbye.')


for parser in (login_parser, main_parser):
    parser.command('quit', 'quit', '@quit')(do_quit)
