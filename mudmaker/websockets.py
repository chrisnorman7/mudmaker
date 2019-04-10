"""Provides the Connection class and other websocket paraphernalia."""

from json import dumps

from autobahn.twisted.websocket import WebSocketServerProtocol


class Connection(WebSocketServerProtocol):
    """A protocol to use with a web client."""

    def __init__(self, game, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.game = game

    def disconnect(self, text=None):
        """Close this websocket, sending text as reason."""
        self.sendClose(code=self.CLOSE_STATUS_CODE_NORMAL, reason=text)

    def onOpen(self):
        """Web socket is now open."""
    def on_connect(self):
        self.status = None
        self.auth_state = AuthenticationState()
        self.ping_time = None
        self.last_active = 0
        self.object_id = None
        self.transport.setTcpNoDelay(True)
        peer = self.transport.getPeer()
        self.host = peer.host
        self.port = peer.port
        self.logger = getLogger(f'{self.host}:{self.port}')
        self.logger.info('Connected.')
        connections.setdefault(None, []).append(self)
        self.set_title(options['name'])
        self.set_prompt_text('Username')
        self.message(options['welcome_msg'])

    def onMessage(self, payload, is_binary):
        if not is_binary:
            self.handle_string(payload)

    def connectionLost(self, reason):
        super().connectionLost(reason)
        self.on_disconnect(reason)

    def send(self, name, *args):
        """Send JSON to the player's browser."""
        data = dict(name=name, args=args)
        json = dumps(data)
        self.sendMessage(json.encode())
        return super().send(name, *args)


class MyWebSocketServerFactory(WebSocketServerFactory):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setProtocolOptions(perMessageCompressionAccept=self.accept)
        self.protocol = Connection

    def accept(self, offers):
        """Accept offers from the browser."""
        for offer in offers:
            if isinstance(offer, PerMessageDeflateOffer):
                return PerMessageDeflateOfferAccept(offer)
