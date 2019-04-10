"""An empty game which simply listens."""

from logging import basicConfig

from mudmaker import Game

game = Game()

if __name__ == '__main__':
    basicConfig(level='INFO')
    game.run()
