"""Provides the Game class."""

import os.path

from datetime import datetime
from json import dumps

from attr import attrs, attrib, Factory
from autobahn.twisted.websocket import listenWS, WebSocketServerFactory
from twisted.internet import reactor
from twisted.web.resource import Resource
from twisted.web.server import Site
from twisted.web.static import File
from twisted.web.util import redirectTo
from yaml import dump, FullLoader, load

from .account_store import AccountStore
from .base import BaseObject
from .directions import Direction
from .objects import Object
from .rooms import Room
from .websockets import WebSocketConnection
from .zones import Zone

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
class ObjectValue:
    """A dumped database object."""

    id = attrib()


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
    max_id = attrib(default=Factory(int), init=False)
    bases = attrib(default=Factory(dict), init=False, repr=False)
    _bases = attrib(default=Factory(dict), repr=False, init=False)
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
    filename = attrib(default=Factory(lambda: 'game.yaml'))

    def __attrs_post_init__(self):
        """Mainly used to add directions."""
        if self.logger is None:
            from logging import basicConfig, getLogger
            basicConfig(level='INFO')
            self.logger = getLogger(__name__)
        for name, cls in (
            ('Base Object', Object),
            ('Base Room', Room),
            ('Base Zone', Zone)
        ):
            self.logger.info('Registering base %s.', name)
            self.register_base(name)(cls)
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
                'Added direction %s with coordinates (%d, %d, %d).', name, d.x,
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
        if os.path.isfile(self.filename):
            self.logger.info('Loading database from %s.', self.filename)
            self.load()
        else:
            self.logger.info('Starting with blank database.')
        self.start_listening()
        reactor.run()
        self.logger.info('Dumping the database to %s.', self.filename)
        self.logger.info(
            'Dumping accounts to %s.', self.account_store.filename
        )
        self.account_store.dump()

    def register_base(self, name):
        """Decorate a class to have it registered as a possible base."""

        def inner(cls):
            self.bases[name] = cls
            self._bases[cls.__name__] = cls
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

    @property
    def players(self):
        """Return a list of players."""
        return [x for x in self.objects.values() if x.account is not None]

    def dump_value(self, value):
        """Dump a singl object, paying particular attention to database
        objects."""
        cls = type(value)
        if cls is list:
            return [self.dump_value(element) for element in value]
        elif cls is dict:
            return {
                self.dump_value(name): self.dump_value(data) for (
                    name, data
                ) in value.items()
            }
        elif issubclass(cls, BaseObject):
            return ObjectValue(value.id)
        else:
            return value

    def load_value(self, data):
        """Load a single value from data, paying particular attention to
        database objects."""
        if isinstance(data, list):
            return [self.load_value(element) for element in data]
        elif isinstance(data, dict):
            return {
                self.load_value(name): self.load_value(value) for (
                    name, value
                ) in data.items()
            }
        elif isinstance(data, ObjectValue):
            return self._objects[data.id]
        else:
            return data

    def as_dict(self):
        """Return a dictionary which can be dumped to save the state of this
        game."""
        return self.dump_value(
            dict(objects=[o.dump() for o in self._objects.values()])
        )

    def dump(self):
        """Dump game state to disk."""
        with open(self.filename, 'w') as f:
            dump(self.as_dict(), stream=f)

    def from_dict(self, data):
        """Load the data loaded with self.load."""
        if self._objects:
            raise RuntimeError(
                'Attempting to load objects into a non-empty game.'
            )
        attributes = {}
        for row in data.get('objects', []):
            class_name = row['class_name']
            bases = row['bases']
            bases = tuple(self._bases[name] for name in bases)
            a = row.get('attributes', {})
            id = a.pop('id', None)
            self.make_object(class_name, bases, id=id)
            self.max_id = max(self.max_id, id)
            attributes[id] = a
        for id, a in attributes.items():
            obj = self._objects[id]
            for name, value in a.items():
                setattr(obj, name, self.load_value(value))

    def load(self):
        """Load some yaml and run it through self.from_dict."""
        with open(self.filename, 'r') as f:
            data = load(f, Loader=FullLoader)
        self.from_dict(data)
