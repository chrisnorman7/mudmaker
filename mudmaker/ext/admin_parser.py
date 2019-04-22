"""Provides admin_parser."""

from code import InteractiveConsole
from contextlib import redirect_stdout, redirect_stderr

from twisted.internet import reactor

from .builder_parser import builder_parser
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
def shell(player):
    """Evaluate some code."""
    s = Shell(player)
    player.message('*** Python Shell ***')
    player.message('Type a full stop on a blank line to exit.')
    player.message('>>>')
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
