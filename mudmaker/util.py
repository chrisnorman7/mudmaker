"""Uitlity functions."""

from traceback import format_exception


def format_error(e):
    """Return a string representing an error."""
    return ''.join(format_exception(e.__class__, e, e.__traceback__))


def english_list(l, empty='nothing', key=str, sep=', ', and_='and '):
    """Return a decently-formatted list."""
    results = [key(x) for x in l]
    if not results:
        return empty
    elif len(results) == 1:
        return results[0]
    else:
        res = ''
        for pos, item in enumerate(results):
            if pos == len(results) - 1:
                res += '%s%s' % (sep, and_)
            elif res:
                res += sep
            res += item
        return res


def yes_or_no(response):
    """Return True if response is yes, y, or ye, False otherwise."""
    return response in ('y', 'ye', 'yes')


def broadcast(connections, text):
    """Broadcast a message to everyone connected to the game."""
    for id, con in connections.items():
        if id is None:
            continue
        con.message(text)


def pluralise(n, singular, plural=None):
    """Return singular if n == 1 else plural."""
    if plural is None:
        plural = singular + 's'
    if n == 1:
        return singular
    return plural


def format_timedelta(td):
    """Format timedelta td."""
    fmt = []  # The format as a list.
    seconds = td.total_seconds()
    years, seconds = divmod(seconds, 31536000)
    if years:
        fmt.append('%d %s' % (years, 'year' if years == 1 else 'years'))
    months, seconds = divmod(seconds, 2592000)
    if months:
        fmt.append('%d %s' % (months, 'month' if months == 1 else 'months'))
    days, seconds = divmod(seconds, 86400)
    if days:
        fmt.append('%d %s' % (days, 'day' if days == 1 else 'days'))
    hours, seconds = divmod(seconds, 3600)
    if hours:
        fmt.append('%d %s' % (hours, 'hour' if hours == 1 else 'hours'))
    minutes, seconds = divmod(seconds, 60)
    if minutes:
        fmt.append(
            '%d %s' % (
                minutes,
                'minute' if minutes == 1 else 'minutes'
            )
        )
    if seconds:
        fmt.append('%.2f seconds' % seconds)
    return english_list(fmt)
