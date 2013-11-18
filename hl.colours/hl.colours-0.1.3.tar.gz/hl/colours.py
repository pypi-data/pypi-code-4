def _wrap_with(code, bold=False):

    def inner(text, bold=bold):
        c = code
        if bold:
            c = "1;%s" % c
        return "\033[%sm%s\033[0m" % (c, text)
    return inner


COLORS = {
    'red': 31,
    'green': 32,
    'yellow': 33,
    'blue': 34,
    'magenta': 35,
    'cyan': 36,
    'white': 37
}


for color, value in COLORS.items():
    globals()[color] = _wrap_with(value)
    globals()['b%s' % color] = _wrap_with(value, bold=True)


__all__ = COLORS.keys()

