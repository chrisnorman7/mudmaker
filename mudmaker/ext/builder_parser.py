"""Provides builder_parser."""

from functools import partial

from ..menus import Menu
from ..parsers import main_parser
from ..rooms import Room
from ..util import yes_or_no

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
            player.message('Created exit %s.' % x)
            x = room.link(location, d.opposite)
            player.message('Created entrance %s.' % x)


def rename_room(location, obj):
    obj.message('Enter the new room name:')
    if location.name is not None:
        obj.connection.set_input_text(location.name)
    name = yield
    if name:
        location.name = name
        obj.message('Done.')
    else:
        obj.message('Names cannot be blank.')


def describe_room(location, obj):
    obj.message('Enter the new description:')
    obj.connection.set_input_type('textarea')
    if location.description is not None:
        obj.connection.set_input_text(location.description)
    description = yield
    if not description:
        description = None
    location.description = description
    obj.message('Done.')


def delete_room(location, obj):
    obj.message('Are you sure you want to delete this room?')
    res = yield
    if yes_or_no(res):
        if len(location.contents) != 1:
            obj.message('You cannot delete this room because it s not empty.')
        elif not location.exits:
            obj.message(
                'There is no exit to move you through. Dig an exit then try '
                'again.'
            )
        else:
            location.exits[0].use(obj)
            for exit in location.exits + location.entrances:
                obj.message('Deleting exit %s.' % exit)
                exit.delete()
            location.delete()
            obj.message('Done.')
    else:
        obj.message('Cancelled.')


@builder_parser.command('redit', '@redit', '@room-edit')
def do_redit(player, location):
    """Edit the current room."""
    if location is None:
        player.message('You are nowhere fit for editing.')
        return

    def before_send(m, obj):
        m.items.clear()
        m.header = str(location) + '\n' + location.get_description()
        m.add_item('Rename', partial(rename_room, location))
        m.add_item('Change Description', partial(describe_room, location))
        m.add_item('Delete Room', partial(delete_room, location))

    yield from Menu(
        'Room Editor'
    ).send_forever(player, before_send=before_send)
