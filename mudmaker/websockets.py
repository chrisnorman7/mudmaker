"""Provides the Connection class and other websocket paraphernalia."""

from inspect import isgenerator
from json import dumps
from logging import getLogger
from time import time

from attr import attrs, attrib, Factory
from autobahn.twisted.websocket import WebSocketServerProtocol
from commandlet.exc import CommandFailedError

from .exc import DontSaveCommand
from .parsers import login_parser
from .socials import factory
from .util import format_error


@attrs
class InputType:
    """Stores the input type along with a timestamp representing when the last
    change was made."""

    type = attrib()
    stamp = attrib(default=Factory(time))


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
        self.game.connections.append(self)
        self.parser = login_parser
        self.ping_time = None
        self.last_active = 0
        self.object = None
        self.input_type = InputType('text')
        self.status = None
        self.title = None
        self.prompt_text = None
        peer = self.transport.getPeer()
        self.host = peer.host
        self.port = peer.port
        self.logger = getLogger(f'{self.host}:{self.port}')
        self.logger.info('Connected.')
        self.set_title(self.game.name)
        self.set_prompt_text('Login Command')
        self.message(self.game.welcome_msg)

    def onMessage(self, payload, is_binary):
        if not is_binary:
            self.handle_string(payload.decode())

    def send_status(self):
        """Send the attached object's status HTML."""
        html = '<p>Not yet implemented.</p>'
        if html != self.status:
            self.status = html
            self.send('status', html)

    def set_input_type(self, t='text'):
        """Set the input type. Valid options are anything that can be recognised
        by the type attribute of the html input tag."""
        if t != self.input_type.type:
            if t == 'password':
                self.set_prompt_text('Password')
            self.send('inputType', t)
        self.input_type = InputType(t)

    def set_input_text(self, t):
        """Set the input text to t."""
        self.send('inputText', t)

    def get_password(self, message):
        """Tell the client to hide input, and send the message to the user.
        Next time input is received, tell the client to unhide the input."""
        self.set_input_type('password')
        self.message(message)

    def set_prompt_text(self, p):
        """Tell the client to use p as the new prompt text."""
        if p != self.prompt_text:
            self.prompt_text = p
            self.send('promptText', p)

    def set_title(self, t):
        """Tell the client to set the title to t."""
        if self.title != t:
            self.title = t
            self.send('title', t)

    def get_context(self):
        """Get a context to be sent to self.parser."""
        player = self.object
        if player is None:
            is_staff = False
            account = None
            location = None
            zone = None
        else:
            account = player.account
            is_staff = account.is_staff
            location = player.location
            if location is None:
                zone = None
            else:
                zone = location.zone
        return dict(
            con=self, player=player, hostname=self.host, port=self.port,
            host='%s:%d' % (self.host, self.port), game=self.game,
            parser=self.parser, logger=self.logger,
            accounts=self.game.account_store, is_staff=is_staff,
            account=account, location=location, socials=factory, zone=zone
        )

    def use_exit(self, direction):
        """Use the exit in the given direction."""
        player = self.object
        location = player.location
        x = location.match_exit(direction)
        if x is None:
            player.message('You cannot go that way.')
        else:
            x.use(player)

    def huh(self, string, tried_commands):
        """Called when no command was found. The tried_commands variable might
        contain already-tried commands."""
        here = self.object.location
        if here is not None:
            if string in self.game.directions:
                self.use_exit(self.game.directions[string])
                return
            if here.parser is not None:
                try:
                    here.parser.handle_command(string, **self.get_context())
                    return  # We're done here.
                except CommandFailedError as e:
                    tried_commands.extend(e.tried_commands)
        self.message('No command found.')
        if tried_commands:
            possible_commands = ', '.join(
                map(lambda thing: thing.name, tried_commands)
            )
            self.message(
                'Commands you may have meant to try: %s.' % possible_commands
            )

    def handle_string(self, string):
        """Handle a string as a command."""
        last_input_type = self.input_type
        self.last_active = time()
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
                ctx = self.get_context()
                try:
                    res = self.parser.handle_command(string, **ctx)
                    if isgenerator(res):
                        try:
                            next(res)
                            self.command_result = res
                        except StopIteration:
                            pass  # It just finished prematurely.
                except DontSaveCommand:
                    save_command = False
                except CommandFailedError as e:
                    self.huh(string, e.tried_commands)
                finally:
                    if save_command:
                        self.last_command = string
        except Exception as e:
            self.logger.exception('Command %r threw an error:', string)
            self.message(self.game.error_msg)
            if self.object and self.object.account.is_staff:
                self.message(format_error(e))
        finally:
            self.send_status()
            if self.input_type is last_input_type and \
               last_input_type.type != 'text':
                # Only reset back to text if no changes to the input type have
                # been made this run, the input type is not "text", and there
                # is no command still running.
                print('Reset input type.')
                self.set_input_type()
            else:
                print('Don\'t reset input type.')

    def connectionLost(self, reason):
        super().connectionLost(reason)
        self.logger.info(reason.getErrorMessage())
        if self in self.game.connections:
            self.game.connections.remove(self)
        if self.object is not None:
            self.object.connection = None

    def send(self, name, *args):
        """Send JSON to the player's browser."""
        data = dict(name=name, args=args)
        json = dumps(data)
        self.sendMessage(json.encode())
        self.send_status()

    def message(self, text):
        """Send some text to this connection."""
        return self.send('message', text)
