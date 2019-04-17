from mudmaker import Zone


def test_init(game, zone):
    assert isinstance(zone, Zone)
    assert zone.game is game
    assert zone.rooms == []
    assert game.zones[zone.id] is zone
