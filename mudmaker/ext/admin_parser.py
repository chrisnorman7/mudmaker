"""Provides admin_parser."""

from code import InteractiveConsole
from contextlib import redirect_stdout, redirect_stderr
from functools import partial

from twisted.internet import reactor

from .builder_parser import builder_parser
from ..menus import Menu
from ..socials import Social
from ..util import yes_or_no, broadcast


class Shell(InteractiveConsole):
    def __init__(self, player, *args, **kwargs):
        self.player = player
        kwargs['locals'] = player.connection.get_context()
        for name, cls in player.game._bases.items():
            kwargs['locals'][name] = cls
        super().__init__(*args, **kwargs)

    def push(self, line):
        """Push code, but store the object first."""
        with redirect_stdout(self), redirect_stderr(self):
            res = super().push(line)
        return res

    def write(self, text):
        """Send the text to self.connections."""
        self.player.message(text)


admin_parser = builder_parser.copy()


@admin_parser.command('shell', '@shell', '@python')
def shell(player, con):
    """Evaluate some code."""
    s = Shell(player)
    player.message('*** Python Shell ***')
    player.message('Type a full stop on a blank line to exit.')
    player.message('>>>')
    prompt = con.prompt_text
    con.set_prompt_text('Code')
    while True:
        line = yield
        if line == '.':
            break
        try:
            if s.push(line):
                p = '...'
            else:
                p = '>>>'
            player.message(p)
        except SystemExit:
            player.message('SystemExit.')
            break
    con.set_prompt_text(prompt)
    player.message('Exiting.')


@admin_parser.command('@shutdown <reason>')
def shutdown(con, player, game, reason):
    """Shutdown the server."""
    player.message('Are you sure you want to shutdown the server now?')
    res = yield
    if yes_or_no(res):
        reason = reason.capitalize()
        con.logger.info('Shutdown initiated:')
        con.logger.info(reason)
        broadcast(game.connections, f'The server is shutting down:\n{reason}')
        reactor.callLater(1.0, reactor.stop)
    else:
        player.message('Cancelled.')


@admin_parser.command('@broadcast <message>')
def do_message(game, player, message):
    """Send a message to everyone connected."""
    broadcast(game.players, '%s broadcasts: %s' % (player.name, message))


def edit_string(social, name, obj):
    obj.message('Enter the new value:')
    value = yield
    if value:
        setattr(social, name, value)


def delete_social(social, obj):
    obj.message('Are you sure you want to delete this social?')
    res = yield
    if yes_or_no(res):
        social.delete()
        obj.message('Done.')
    else:
        obj.message('cancelled.')


def edit_social(social, obj):
    """Edit a social."""
    m = Menu(f'Edit {social.name}')

    def before_send(self, obj):
        self.header = social.description
        self.items.clear()
        self.add_item(
            f'With no target: {social.no_target}', partial(
                edit_string, social, 'no_target'
            )
        )
        self.add_item(
            f'With self as target: {social.self_target}', partial(
                edit_string, social, 'self_target'
            )
        )
        self.add_item(
            f'With any other target: {social.any_target}', partial(
                edit_string, social, 'any_target'
            )
        )
        self.add_label('Actions')
        self.add_item('Delete', partial(delete_social, social))

    yield from m.send_forever(obj, before_send=before_send)


def add_social(obj):
    obj.message('Social name:')
    name = yield
    obj.message(
        'The string to be used when the social is used with no target:'
    )
    no_target = yield
    obj.message(
        'The string to be used when the social is used with the object as the '
        'target:'
    )
    self_target = yield
    obj.message(
        'The string to be used when the social is used with any other target:'
    )
    any_target = yield
    if all((name, no_target, self_target, any_target)):
        obj.game.make_object(
            'Social', (Social,), name=name, no_target=no_target,
            self_target=self_target, any_target=any_target
        )
        obj.message('Done.')
    else:
        obj.message('All fields are required.')


@admin_parser.command('edit-socials', '@edit-socials')
def do_edit_socials(player, game):
    """Edit socials."""
    m = Menu('Socials')

    def before_send(self, obj):
        self.items.clear()
        self.add_label('Existing Socials')
        for social in sorted(game.socials.values(), key=lambda s: s.name):
            self.add_item(social.name.title(), partial(edit_social, social))
        self.add_label('Actions')
        self.add_item('Add Social', add_social)

    yield from m.send_forever(player, before_send=before_send)
