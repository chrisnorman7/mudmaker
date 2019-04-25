"""Provides the two main command parsers: login_parser, and main_parser."""

from datetime import datetime

from commandlet import Parser, command
from .exc import AuthenticationError
from .objects import Object
from .socials import Social
from .util import get_login


class MudMakerParser(Parser):
    """A parser with extra socials."""

    def social(
        self, name, no_target, self_target, any_target, description=None
    ):
        """Add a social to this parser. The name argument will be the name of
        the command. If None, the description argument will become '<name> at
        someone.'. All other arguments must be social strings. They will be
        used as follows:

        no_target: When the command is used with no arguments.
        self.target: When the object that performed the command is the
        argument.
        any_target: Any other object is passed.
        """
        if description is None:
            description = '%s at something.' % name
        s = Social(no_target, self_target, any_target)
        s.__doc__ = description
        self.command(name)(s)
        self.command(name, '%s <object:target>' % name)(s)


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


main_parser.social(
    'smile', '%1N smile%1s.', '%1N smile%1s broadly.', '%1N smile%1s at %2n.'
)

main_parser.social(
    'nod', '%1N nod%1s.', '%1N nod%1s emphatically.', '%1N nod%1s to %2n.'
)


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
        game.finish_login(con, player)
    except AuthenticationError:
        con.logger.info('Attempted to login as %s.', username)
        con.message('Invalid username or password.')


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
