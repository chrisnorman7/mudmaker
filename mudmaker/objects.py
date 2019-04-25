"""Provides the Object class."""

from .base import BaseObject, LocationMixin
from .exc import NoSuchObjectError


class Object(BaseObject, LocationMixin):
    """An object in the database."""

    @classmethod
    def on_init(cls, instance):
        """Add this object to self.game.objects."""
        instance.game.objects[instance.id] = instance
        instance.connection = None
        instance.parser = None

    @property
    def account(self):
        """Get any account object associated with this object."""
        try:
            return self.game.account_store.account_for(self)
        except NoSuchObjectError:
            pass  # return None.

    def message(self, text):
        """Send some text to this object's connection."""
        if self.connection is not None:
            self.connection.message(text)
            return True
        return False

    def look_here(self):
        """Have this object look at its surroundings."""
        here = self.location
        self.message('[%s; %s]' % (here.zone.name, here.name))
        self.message(here.get_description())

    def no_location_match(self, string):
        """No matches may be performed at this location. By default, sends a
        message to this object explaining that."""
        self.message('You cannot see anything here.')

    def no_match(self, string):
        """No match was found. By default, a message explaining that is sent to
        this object."""
        self.message('I don\'t see "%s" here.' % string)

    def multiple_matches(self, string, objects):
        """Multiple matches were found. By default, send a message explaining
        that to this object."""
        self.message('I don\'t know which "%s" you mean.' % string)

    def match_object(self, obj, string):
        """See if obj matches string."""
        if string == "me" and obj is self:
            return True
        elif obj.name.lower().startswith(string.lower()):
            return True
        return False

    def single_match(self, string, objects=None):
        """Return a single match from the given list of objects. If objects is
        None, self.location.contents will be used.

        If objects is None, and this object has no location, the result of
        calling self.no_location_match with string will be returned.

        If the match string is "me", then this object will be considered in the
        match if it is in the list of objects.

        If no matches are found, then the result of calling self.no_match with
        string will be returned.

        If multiple matches are found, then the result of calling
        self.multiple_matches with string and the list of objects that were
        matched will be returned.

        If this object is a member of staff, and the string starts with a hash
        symbol (#), the remaining string will be considered an object ID, and
        the object with that ID will be returned."""
        if self.account.is_staff and string.startswith('#'):
            try:
                id = int(string[1:])
                return self.game.objects[id]
            except (ValueError, KeyError):
                return self.no_match(string)
        if objects is None:
            if self.location is None:
                return self.no_location_match(string)
            else:
                objects = self.location.contents
        results = []
        results = [x for x in objects if self.match_object(x, string)]
        if len(results) == 1:
            return results[0]
        elif not results:
            return self.no_match(string)
        else:
            return self.multiple_matches(string, results)
