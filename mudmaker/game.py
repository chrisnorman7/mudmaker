"""Provides the Game class."""

from json import dumps
from logging import getLogger

from attr import attrs, attrib, Factory
from autobahn.twisted.websocket import (
    listenWS, WebSocketServerFactory, WebSocketServerProtocol
)
from twisted.internet import reactor
from twisted.web.resource import Resource
from twisted.web.server import Site
from twisted.web.static import File
from twisted.web.util import redirectTo

NoneType = type(None)
static = File('html')


class GameResource(Resource):
    """A resource that stores a reference to the game it's attached to."""

    isLeaf = True

    def __init__(self, game, *args, **kwargs):
        self.game = game
        super().__init__(*args, **kwargs)


class WebSocketPage(GameResource):
    """This resource is used so that the JavaScript portion of the site doesn't
    have to guess the websocket port."""

    def render_GET(self, request):
        """Calls game.on_websocket_page with the given request."""
        return self.game.on_websocket_page(request)


class IndexPage(GameResource):
    """Returns the index page for a given game."""

    def render_GET(self, request):
        """Calls game.on_index_page with the given request."""
        return self.game.on_index_page(request)


@attrs
class Game:
    """A game instance."""

    interface = attrib(default=Factory(lambda: '127.0.0.1'))
    http_port = attrib(default=Factory(lambda: 4000))
    logger = attrib(default=Factory(lambda: getLogger(__name__)))
    websocket_class = attrib(default=Factory(lambda: WebSocketServerProtocol))
    websocket_factory = attrib(default=Factory(NoneType))
    websocket_port = attrib(default=Factory(NoneType))
    site_port = attrib(default=Factory(NoneType))
    web_root = attrib(default=Factory(Resource))
    connections = attrib(default=Factory(list), init=False)
    zones = attrib(default=Factory(list), init=False)
    rooms = attrib(default=Factory(list), init=False)
    objects = attrib(default=Factory(list), init=False)

    def on_websocket_page(self, request):
        """Return the websocket port number."""
        return dumps(self.websocket_port.port).encode()

    def on_index_page(self, request):
        """Get the index page. By default redirects to /static/index.html."""
        return redirectTo(b'/static/index.html', request)

    def start_listening(self):
        """Start listening for network connections. Usually called from
        Game.run."""
        self.logger.info('Adding web socket page.')
        self.web_root.putChild(b'wsport', WebSocketPage(self))
        self.logger.info('Adding index page.')
        self.web_root.putChild(b'', IndexPage(self))
        self.logger.info('Adding static page.')
        self.web_root.putChild(b'static', static)
        if self.websocket_factory is None:
            self.websocket_factory = WebSocketServerFactory(
                f'ws://{self.interface}:{self.http_port + 1}'
            )
            self.websocket_factory.protocol = self.websocket_class
        self.websocket_port = listenWS(
            self.websocket_factory, interface=self.interface
        )
        self.logger.info(
            'Listening for websockets on %s:%d.',
            self.websocket_port.interface, self.websocket_port.port
        )
        site = Site(self.web_root)
        self.site_port = reactor.listenTCP(
            self.http_port, site, interface=self.interface
        )

    def run(self):
        """Start this game listening, and start the reactor."""
        self.start_listening()
        reactor.run()
