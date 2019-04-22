"""Provides builder_parser."""

from ..parsers import main_parser

builder_parser = main_parser.copy()


@builder_parser.command('@undig <direction>', '@destroy-exit <direction>')
def undig(player, location, direction):
    """Remove the exit in the given direction."""
    if location is None:
        player.message('You cannot do that here.')
    else:
        e = location.match_exit(direction)
        if e is None:
            player.message('There is no exit in that direction.')
        else:
            o = e.other_side
            if o is not None:
                player.message('Deleted %s.' % o)
                o.delete()
            e.delete()
            player.message('Deleted %s.' % e)
