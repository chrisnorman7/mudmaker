from mudmaker import Zone


def test_init(game, zone):
    assert isinstance(zone, Zone)
    zone.game = game
    assert zone.rooms == []
