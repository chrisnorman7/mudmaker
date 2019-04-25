from mudmaker import Object


def test_match_object(obj):
    assert obj.match_object(obj, 'me') is True
    assert obj.match_object(obj, obj.name) is True
    assert obj.match_object(obj, 'Nope') is False


def test_single_match_works(player, game):
    assert player.location is not None
    other = game.make_object(
        'Object', (Object,), name='Other', location=player.location
    )
    assert player.single_match('me') is player
    assert player.single_match(player.name) is player
    assert player.single_match('other') is other


def test_single_match_fails(player, game):
    con = player.connection
    string = 'fails'
    assert player.single_match(string) is None
    assert con.last_message == 'I don\'t see "%s" here.' % string
    game.make_object(
        'Object', (Object,), name='Menu', location=player.location
    )
    assert player.single_match('me') is None
    assert con.last_message == 'I don\'t know which "me" you mean.'
    player.location = None
    assert player.single_match('me') is None
    assert con.last_message == 'You cannot see anything here.'
