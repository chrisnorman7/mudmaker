from mudmaker import Zone


def test_init(game, zone):
    assert isinstance(zone, Zone)
    assert zone.game is game
    assert zone.rooms == []
    assert game.zones[zone.id] is zone
    assert game._objects[zone.id] is zone


def test_delete(zone, game):
    zone.delete()
    assert zone.id not in game.zones
