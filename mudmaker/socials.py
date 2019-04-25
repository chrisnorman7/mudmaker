"""Provides a PopulatedSocialsFactory instance called factory."""

from attr import attrs, attrib
from emote_utils import PopulatedSocialsFactory

factory = PopulatedSocialsFactory()


@factory.suffix('name', 'n')
def name(obj, suffix):
    """"you" or name."""
    return 'you', obj.name


@factory.suffix('ss', 'your')
def your(obj, suffix):
    """"your" or "name's"."""
    return 'your', f"{obj.name}'s"


@attrs
class Social:
    """A social."""

    no_target = attrib()
    self_target = attrib()
    any_target = attrib()

    def __call__(self, player, target=False):
        """Perform a social as player."""
        if target is None:
            return  # Match failed.
        p = []
        if target is False:
            string = self.no_target
        elif target is player:
            string = self.self_target
        else:
            p = [target]
            string = self.any_target
        player.do_social(string, _perspectives=p)
