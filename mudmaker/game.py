"""Provides the Game class."""

from datetime import datetime
from json import dumps

from attr import attrs, attrib, Factory
from autobahn.twisted.websocket import listenWS, WebSocketServerFactory
from twisted.internet import reactor
from twisted.web.resource import Resource
from twisted.web.server import Site
from twisted.web.static import File
from twisted.web.util import redirectTo

from .account_store import AccountStore
from .base import BaseObject
from .directions import Direction
from .websockets import WebSocketConnection

NoneType = type(None)
static = File('html')


class FunctionResource(Resource):
    """A resource that stores a reference to the game it's attached to."""

    isLeaf = True

    def __init__(self, func, *args, **kwargs):
        """self.func will be called with render_GET."""
        self.func = func
        super().__init__(*args, **kwargs)

    def render_GET(self, request):
        return self.func(request)


@attrs
class Game:
    """A game instance."""

    interface = attrib(default=Factory(lambda: '127.0.0.1'))
    http_port = attrib(default=Factory(lambda: 4000))
    logger = attrib(default=Factory(NoneType), repr=False)
    websocket_class = attrib(default=Factory(lambda: WebSocketConnection))
    websocket_factory = attrib(default=Factory(NoneType), repr=False)
    websocket_port = attrib(default=Factory(NoneType), repr=False)
    site_port = attrib(default=Factory(NoneType), repr=False)
    web_root = attrib(default=Factory(Resource), repr=False)
    connections = attrib(default=Factory(list), init=False, repr=False)
    zones = attrib(default=Factory(dict), init=False, repr=False)
    rooms = attrib(default=Factory(dict), init=False, repr=False)
    objects = attrib(default=Factory(dict), init=False, repr=False)
    exits = attrib(default=Factory(dict), init=False, repr=False)
    max_id = attrib(default=Factory(int), init=False, repr=False)
    bases = attrib(default=Factory(dict))
    welcome_msg = attrib(
        default=Factory(
            lambda: 'You can modify this message by setting game.welcome_msg.'
        )
    )
    error_msg = attrib(
        default=Factory(
            lambda: 'While executing your command an error occurred.'
        )
    )
    started = attrib(default=Factory(datetime.utcnow))
    directions = attrib(default=Factory(dict), repr=False)
    _objects = attrib(default=Factory(dict), init=False, repr=False)
    account_store = attrib(default=Factory(NoneType), repr=False)

    def __attrs_post_init__(self):
        """Mainly used to add directions."""
        if self.logger is None:
            from logging import basicConfig, getLogger
            basicConfig(level='INFO')
            self.logger = getLogger(__name__)
        for name, aliases, coordinates in (
            ('north', ['n'], dict(y=1)),
            ('northeast', ['ne'], dict(x=1, y=1)),
            ('east', ['e'], dict(x=1)),
            ('southeast', ['se'], dict(x=1, y=-1)),
            ('south', ['s'], dict(y=-1)),
            ('southwest', ['sw'], dict(y=-1, x=-1)),
            ('west', ['w'], dict(x=-1)),
            ('northwest', ['nw'], dict(x=-1, y=1)),
            ('up', ['u'], dict(z=1)),
            ('down', ['d'], dict(z=-1))
        ):
            d = self.add_direction(name, *aliases, **coordinates)
            self.logger.info(
                'Added direction %s with coodinates (%d, %d, %d).', name, d.x,
                d.y, d.z
            )
        if self.account_store is None:
            self.account_store = AccountStore(self)

    def new_id(self):
        self.max_id += 1
        return self.max_id

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
        self.web_root.putChild(
            b'wsport', FunctionResource(self.on_websocket_page)
        )
        self.logger.info('Adding index page.')
        self.web_root.putChild(b'', FunctionResource(self.on_index_page))
        self.logger.info('Adding static page.')
        self.web_root.putChild(b'static', static)
        if self.websocket_factory is None:
            self.websocket_factory = WebSocketServerFactory(
                f'ws://{self.interface}:{self.http_port + 1}'
            )
            self.websocket_factory.protocol = self.websocket_class
        self.websocket_factory.game = self
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
        self.logger.info(
            'Listening for HTTP connections on %s:%d.',
            self.site_port.interface, self.site_port.port
        )

    def run(self):
        """Start this game listening, and start the reactor."""
        self.start_listening()
        reactor.run()

    def register_base(self, name):
        """Decorate a class to have it registered as a possible base."""

        def inner(cls):
            self.bases[name] = cls
            return cls

        return inner

    def make_object(self, class_name, bases, **attributes):
        """Make an object - which could be anything - and add it to this game.
        class_name is the name used for the newly-created class, and attributes
        will be passed to the new class's __init__ method."""
        cls = type(class_name, bases, dict(__init__=BaseObject.__init__))
        obj = cls(self, **attributes)
        for base in bases:
            base.on_init(obj)
        self._objects[obj.id] = obj
        return obj

    def add_direction(self, name, *aliases, x=0, y=0, z=0):
        """Add a new direction. You can add as many aliases as you like. These
        will be used as commands to invoke exits. The x, y, and z coordinates
        allow you to set sensible coordinates for rooms should you want to. The
        name of the direction should be a full name like "northeast"."""
        d = Direction(name, x, y, z)
        self.directions[name] = d
        for alias in aliases:
            self.directions[alias] = d
        return d
