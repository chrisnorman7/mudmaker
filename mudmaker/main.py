"""Provides the main entry point."""

from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

from mudmaker.game import Game

interface = Game.__attrs_attrs__[0].default.factory()
port = Game.__attrs_attrs__[1].default.factory()


parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)

parser.add_argument(
    '-i', '--interface', default=interface, help='The interface to bind to'
)

parser.add_argument(
    '-p', '--http-port', type=int, default=port, help='The HTTP port to '
    'listen on'
)


def main():
    args = parser.parse_args()
    game = Game(interface=args.interface, http_port=args.http_port)
    game.run()


if __name__ == '__main__':
    main()
