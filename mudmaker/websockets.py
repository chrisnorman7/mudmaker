"""Provides the Connection class and other websocket paraphernalia."""

from inspect import isgenerator
from json import dumps
from logging import getLogger

from autobahn.twisted.websocket import WebSocketServerProtocol
from commandlet.exc import CommandFailedError

from .exc import DontSaveCommand
from .util import format_error
from .parsers import login_parser


class WebSocketConnection(WebSocketServerProtocol):
    """A protocol to use with a web client."""

    def disconnect(self, text=None):
        """Close this websocket, sending text as reason."""
        self.sendClose(code=self.CLOSE_STATUS_CODE_NORMAL, reason=text)

    def onOpen(self):
        """Web socket is now open."""
        self.last_command = None
        self.command_result = None
        self.game = self.factory.game
        self.parser = login_parser
        self.ping_time = None
        self.last_active = 0
        self.object = None
        peer = self.transport.getPeer()
        self.host = peer.host
        self.port = peer.port
        self.logger = getLogger(f'{self.host}:{self.port}')
        self.logger.info('Connected.')
        self.message(self.game.welcome_msg)

    def onMessage(self, payload, is_binary):
        if not is_binary:
            self.handle_string(payload.decode())

    def handle_string(self, string):
        """Handle a string as a command."""
        try:
            if self.command_result is not None:
                try:
                    self.command_result.send(string)
                except Exception as e:
                    self.command_result = None
                    if not isinstance(e, StopIteration):
                        # The command raised an exception.
                        raise e
            else:
                save_command = True
                try:
                    res = self.parser.handle_command(
                        string, con=self, player=self.object,
                        hostname=self.host, port=self.port,
                        host=self.logger.name, game=self.game,
                        parser=self.parser, logger=self.logger
                    )
                    if isgenerator(res):
                        try:
                            next(res)
                            self.command_result = res
                        except StopIteration:
                            pass  # It just finished prematurely.
                except DontSaveCommand:
                    save_command = False
                except CommandFailedError as e:
                    self.message('No command found.')
                    if e.tried_commands:
                        possible_commands = ', '.join(e.tried_commands)
                        self.message(
                            'Commands you may have meant to try: %s.' %
                            possible_commands
                        )
                finally:
                    if save_command:
                        self.last_command = string
        except Exception as e:
            self.logger.exception('Command %r threw an error:', string)
            self.message(self.game.error_msg)
            if self.object and self.object.account.is_staff:
                self.message(format_error(e))

    def connectionLost(self, reason):
        super().connectionLost(reason)
        self.logger.info(reason.getErrorMessage())

    def send(self, name, *args):
        """Send JSON to the player's browser."""
        data = dict(name=name, args=args)
        json = dumps(data)
        self.sendMessage(json.encode())

    def message(self, text):
        """Send some text to this connection."""
        return self.send('message', text)
