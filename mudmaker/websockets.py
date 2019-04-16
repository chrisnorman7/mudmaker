"""Provides the Connection class and other websocket paraphernalia."""

from json import dumps
from logging import getLogger

from autobahn.twisted.websocket import WebSocketServerProtocol
from commandlet.exc import CommandFailedError

from .parsers import login_parser


class WebSocketConnection(WebSocketServerProtocol):
    """A protocol to use with a web client."""

    def disconnect(self, text=None):
        """Close this websocket, sending text as reason."""
        self.sendClose(code=self.CLOSE_STATUS_CODE_NORMAL, reason=text)

    def onOpen(self):
        """Web socket is now open."""
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
            try:
                self.parser.handle_command(
                    payload.decode(), con=self, player=self.object,
                    hostname=self.host, port=self.port, host=self.logger.name,
                    game=self.game, parser=self.parser
                )
            except CommandFailedError as e:
                self.message('No command found.')
                if e.tried_commands:
                    possible_commands = ', '.join(e.tried_commands)
                    self.message(
                        'Commands you may have meant to try: %s.' %
                        possible_commands
                    )

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
