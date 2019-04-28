"""Provides builder_parser."""

from ..rooms import Room
from ..parsers import main_parser

builder_parser = main_parser.copy()


@builder_parser.command(
    'undig', '@undig <direction>', '@destroy-exit <direction>'
)
def undig(player, location, direction, game):
    """Remove the exit in the given direction."""
    if location is None:
        player.message('You cannot do that here.')
    elif direction not in game.directions:
        player.message('Invalid direction.')
    else:
        d = game.directions[direction]
        e = location.match_exit(d)
        if e is None:
            player.message('There is no exit in that direction.')
        else:
            o = e.other_side
            if o is not None:
                player.message('Deleted %s.' % o)
                o.delete()
            player.message('Deleted %s.' % e)
            e.delete()


@builder_parser.command('dig', '@dig <direction>', '@dig-exit <direction')
def do_dig(player, location, game, zone, direction):
    """Dig an exit in the given direction."""
    if location is None:
        player.message('You cannot dig here.')
    elif direction not in game.directions:
        player.message('Invalid direction.')
    else:
        d = game.directions[direction]
        if location.match_exit(d):
            player.message('There is already a exit in that direction.')
        else:
            coords = d.coordinates_from(location.coordinates)
            rooms = [r for r in zone.rooms if r.coordinates == coords]
            if rooms:
                room = rooms[0]
                player.message('Found room %s.' % room)
            else:
                player.message('Enter the name for the new room:')
                name = yield
                if not name:
                    player.message('Cancelled.')
                    return
                room = game.make_object('Room', (Room,), name=name, zone=zone)
                room.coordinates = coords
            x = location.link(room, d)
            player.message('Created exit %s.' % d)
            x = room.link(location, d.opposite)
            player.message('Created entrance %s.' % x)
