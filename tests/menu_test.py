from mudmaker.menus import Menu, MenuItem, MenuLabel, help_msg


class PretendObject:
    def message(self, string):
        self.string = string


def menu_item(obj):
    pass


def test_menu_item():
    i = MenuItem('Print', print)
    assert i.title == 'Print'
    assert i.func is print


def test_menu_init():
    m = Menu('Test Menu')
    assert m.title == 'Test Menu'
    assert m.items == []
    assert m.help_msg == help_msg


def test_add_item():
    m = Menu('Test Menu')
    i = m.add_item('Test Item', print)
    assert isinstance(i, MenuItem)
    assert i.title == 'Test Item'
    assert i.func is print
    assert len(m.items) == 1


def test_item():
    m = Menu('Test Menu')
    f = m.item('Test Item')(menu_item)
    assert f is menu_item
    assert len(m.items) == 1
    i = m.items[-1]
    assert i.title == 'Test Item'
    assert i.func is f


def test_as_string():
    m = Menu('Test Menu')
    i = m.add_item('Test Item', print)
    assert m.as_string() == f'{m.title}\n\n[1] {i.title}\n{m.prompt_msg}'
    m.header = 'Test'
    assert m.as_string() == (
        f'{m.title}\n\n{m.header}\n[1] {i.title}\n' +
        f'{m.prompt_msg}'
    )


def test_send():
    m = Menu('Test Menu')
    m.add_item('First Item', print)
    m.add_item('Second Item', exec)
    obj = PretendObject()
    m.send(obj)
    assert obj.string == m.as_string()


def test_match():
    obj = PretendObject()
    m = Menu('Test Menu')
    i1 = m.add_item('First Item', print)
    i2 = m.add_item('Second Item', exec)
    i3 = m.add_item('45', getattr)
    assert m.match(obj, '1') is i1
    assert m.match(obj, '2') is i2
    assert m.match(obj, '5') is None  # Number out of range.
    assert obj.string == m.invalid_selection_msg
    delattr(obj, 'string')
    assert m.match(obj, '45') is i3
    assert m.match(obj, '$') is i3
    assert m.match(obj, 'first') is i1
    assert m.match(obj, 'second') is i2
    assert m.match(obj, 'nothing') is None
    assert obj.string == m.invalid_selection_msg


def test_label():
    label = MenuLabel('Test')
    assert label.title == 'Test'
    m = Menu('Testing')
    label = m.add_label('A Label')
    assert m.as_string() == f'{m.title}\n\n-- {label.title} --\n{m.prompt_msg}'


def test_match_with_labels(obj):
    m = Menu('Test Menu')
    m.add_label('Invalid')
    i = m.add_item('Valid', print)
    assert m.match(obj, 'inv') is None
    assert m.match(obj, 'valid') is i
