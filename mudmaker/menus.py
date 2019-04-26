"""Provides the Menu and MenuItem classes."""

from inspect import isgenerator

from attr import attrs, attrib, Factory

help_msg = """To activate items, either type the numbers that appear in \
brackets before each entry, or the first few letters of the title.
If you want the last item in the menu, you can use a dollar ($) sign.
If you want the first item, you can simply press enter.
If you need help, type a question mark (?).
If you wish to abort the menu, type a full stop (.)."""


class MenuDone(Exception):
    """Raise to break out of Menu.send_forever."""


@attrs
class MenuLabel:
    """A label in a menu."""

    title = attrib()


@attrs
class MenuItem(MenuLabel):
    """An item in a menu. Has title and function attributes."""

    func = attrib()


@attrs
class Menu:
    """A menu wich presents the player with various options."""

    title = attrib()
    items = attrib(default=Factory(list))
    header = attrib(default=Factory(type(None)))
    invalid_selection_msg = attrib(
        default=Factory(lambda: 'Invalid selection.')
    )
    prompt_msg = attrib(
        default=Factory(lambda: 'Please enter your selection.')
    )
    help_msg = attrib(default=Factory(lambda: help_msg))
    abort_msg = attrib(default=Factory(lambda: 'Aborted.'))

    def add_label(self, title):
        """Add a label to this menu."""
        label = MenuLabel(title)
        self.items.append(label)
        return label

    def add_item(self, title, func):
        """Add an item to this menu."""
        item = MenuItem(title, func)
        self.items.append(item)
        return item

    def item(self, title):
        """A decorator to add an item.

        Usage::

            m = Menu('Test Menu')

            @m.item('quit')
            def do_quit(obj):
                obj.message('Goodbye.')
                obj.connection.disconnect('Player quit.')
        """

        def inner(func):
            self.add_item(title, func)
            return func

        return inner

    def as_string(self):
        """Return this men as a string."""
        string = self.title
        string += '\n'
        if self.header is not None:
            string += '\n'
            string += self.header
        i = 0
        for item in self.items:
            string += '\n'
            if isinstance(item, MenuItem):
                i += 1
                string += f'[{i}] {item.title}'
            else:
                string += f'-- {item.title} --'
        string += '\n'
        string += self.prompt_msg
        return string

    def send(self, obj):
        """Send this menu to a player."""
        obj.message(self.as_string())

    def match(self, obj, string):
        """Return the first menu item that matches. If there are no matches,
        tell the player that and return None."""
        items = [x for x in self.items if isinstance(x, MenuItem)]
        if string.isnumeric():
            try:
                return items[int(string) - 1]
            except IndexError:
                pass
        if string == '$':
            return items[-1]
        else:
            for item in items:
                if item.title.lower().startswith(string.lower()):
                    return item
            else:
                obj.message(self.invalid_selection_msg)

    def send_forever(self, obj, *args, before_send=None, **kwargs):
        """Keep sending this menu to obj until MenuDone is raised or a full
        stop is received as input. If before_send is not None, it will be
        called with this menu and obj as positional arguments before the menu
        is sent. All extra arguments are sent to self._send_and_handle."""
        while True:
            if before_send is not None:
                before_send(self, obj)
            try:
                yield from self._send_and_handle(obj, *args, **kwargs)
            except MenuDone:
                break

    def _send_and_handle(self, obj, *args, **kwargs):
        """Send this menu to obj, and handle the input. Any found function will
        be called with obj as its first argument, followed by all other args
        and kwargs."""
        self.send(obj)
        res = yield
        if res == '.':
            obj.message(self.abort_msg)
            raise MenuDone()
        elif res == '?':
            obj.message(self.help_msg)
            yield from self._send_and_handle(obj, *args, **kwargs)
        else:
            i = self.match(obj, res)
            if i is not None:
                r = i.func(obj, *args, **kwargs)
                if isgenerator(r):
                    yield from r

    def send_and_handle(self, obj, *args, **kwargs):
        """Send this menu and handle the input using self._send_and_handle.
        This method catches the MenuDone except which is raised as a result of
        typing a full stop on a blank line. All extra arguments are sent along
        to self._send_and_handle as well."""
        try:
            yield from self._send_and_handle(obj, *args, **kwargs)
        except MenuDone:
            pass
