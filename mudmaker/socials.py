"""Provides a PopulatedSocialsFactory instance called factory."""

from emote_utils import PopulatedSocialsFactory

from .attributes import Attribute
from .base import BaseObject
from .parsers import main_parser

factory = PopulatedSocialsFactory()


@factory.suffix('name', 'n')
def name(obj, suffix):
    """"you" or name."""
    return 'you', obj.get_name()


@factory.suffix('ss', 'your')
def your(obj, suffix):
    """"your" or "name's"."""
    return 'your', f"{obj.name}'s"


class Social(BaseObject):
    """A social."""

    no_target = Attribute(
        None, 'The string to be used when no target is specified'
    )
    self_target = Attribute(
        None, 'The string to be used when an object supplies themself as the '
        'target'
    )
    any_target = Attribute(
        None, 'The string to be used for any target not covered by the other '
        'two strings'
    )

    @classmethod
    def on_init(cls, instance):
        instance.game.socials[instance.name] = instance
        if instance.description is None:
            instance.description = f'{instance.name} at someone or something.'
        main_parser.social(instance)

    def use_nothing(self, player):
        player.do_social(self.no_target)

    def use_target(self, player, target):
        """Perform a social as player."""
        if target is player:
            p = []
            string = self.self_target
        else:
            p = [target]
            string = self.any_target
        player.do_social(string, _perspectives=p)

    @classmethod
    def on_delete(cls, instance):
        commands = []
        for cmd in main_parser.commands:
            if getattr(cmd.func.func, 'func', None) not in (
                instance.use_nothing, instance.use_target
            ):
                commands.append(cmd)
        main_parser.commands = commands
        del instance.game.socials[instance.name]
