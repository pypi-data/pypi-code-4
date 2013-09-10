
# Start on an easier-to-use maker for regular expressions,
# so they're not so difficult to construct correctly.


def named(name, expr):
    return "(?P<{0}>{1})".format(name, expr)


def group(expr):
    return "({0})".format(expr)


def whitespace(count='*'):
    return '\s' + count

ws = whitespace


def start(lstrip=True):
    return '^' + ('\s*' if lstrip else '')


def stop(rstrip=True):
    return ('\s*' if rstrip else '') + '$'

word = '\w+'


def full():
    return start() + named('one', word) + ws() + named('two', word + '\d+') + stop()

print full()