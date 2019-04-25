"""Provides a PopulatedSocialsFactory instance called factory."""

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
