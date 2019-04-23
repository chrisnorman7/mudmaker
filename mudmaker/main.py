"""Provides the main entry point."""

from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

from mudmaker.game import Game

game = Game()

parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)

parser.add_argument(
    '-i', '--interface', default=game.interface, help='The interface to bind '
    'to'
)

parser.add_argument(
    '-p', '--http-port', type=int, default=game.http_port, help='The HTTP '
    'port to listen on'
)


def main():
    args = parser.parse_args()
    for name in ('interface', 'http_port'):
        setattr(game, name, getattr(args, name))
    game.run()


if __name__ == '__main__':
    main()
