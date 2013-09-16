
import six
import os
from say import Say, fmt, stdout, caller_fmt, FmtException
import pytest

globalvar = 99


def setup():
    global say
    say = Say(retvalue=True)


def test_basic(param='Yo'):
    setup()

    greeting = "hello"
    assert say("{greeting}, world!") == "{0}, world!".format(greeting)
    assert say("'{greeting}' has {len(greeting)} characters") == "'{0}' has {1} characters".format(greeting, len(greeting))
    assert say("{param}") == "{0}".format(param)
    assert say("{greeting:<10}") == "{0:<10}".format(greeting)
    assert say("{greeting:>20}") == "{0:>20}".format(greeting)

    status = "OK"
    assert say("This is {status}", silent=True) == "This is OK"


def test_gt():
    setup()

    x = 555
    assert (say > "{x} is a big number!") == "555 is a big number!"


def test_hr_and_title():
    setup()

    say.title('say testing follows')
    say.hr(vsep=1)

    # http://en.wikipedia.org/wiki/Box-drawing_character
    say.hr(sep=six.u('\u2504'))
    say.hr(sep=six.u('\u2509'))
    say.hr(sep=six.u('\u2550'))
    say.hr(sep=six.u('\u2591'))
    say.hr(sep=six.u('\u25EF '))
    say.hr(sep=six.u('\u25C9 '))


def test_localvar():
    setup()

    m = "MIGHTY"
    assert say(m) == "MIGHTY"
    assert say("{m}") == "MIGHTY"
    globalvar = "tasty"    # override global var
    assert say(globalvar) == "tasty"
    assert say("{globalvar}") == "tasty"


def test_globalvar():
    setup()

    assert say("{globalvar}") == str(globalvar)


def test_unicode():
    setup()

    u = six.u('This\u2014is Unicode!')
    assert say(u) == u
    assert say("Hey! {u}") == six.u('Hey! This\u2014is Unicode!')
    too = "too"
    assert say(six.u("Unicode templates {too}")) == six.u("Unicode templates too")

def test_format_string():
    setup()

    x = 33.123456789
    assert say("{x} is floating point!") == '33.123456789 is floating point!'
    assert say("{x:0.2f} is shorter") == '33.12 is shorter'
    assert say("{x:8.3f} is in the middle") == '  33.123 is in the middle'


def test_fmt():
    setup()

    v = 1212

    assert say("++{v}") == fmt("++{v}")
    # should print only once


def test_encoded_encoding():
    setup()
    say.set(encoding='base64', encoded=True)
    assert say('I am a truck!') == "SSBhbSBhIHRydWNrIQo="
    assert say('I am a truck!', encoding='rot-13') == 'V nz n gehpx!'
    assert say('V nz n gehpx!', encoding='rot-13') == 'I am a truck!'


def test_files(tmpdir):
    say = Say()

    tmpfile = tmpdir.join('test.txt')
    say.setfiles([stdout, tmpfile])
    say("Yowza!")

    assert tmpfile.read() == "Yowza!" + "\n"


def test_example_1():
    setup()

    x = 12
    nums = list(range(4))

    assert say("There are {x} things.") == "There are 12 things."
    assert say("Nums has {len(nums)} items: {nums}") == "Nums has 4 items: [0, 1, 2, 3]"

def test_example_2():
    setup()

    errors = [{'name': 'I/O Error', 'timestamp': 23489273},
              {'name': 'Compute Error', 'timestamp': 349734289}]

    say.title('Errors')
    for i, e in enumerate(errors, start=1):
        say("{i:3}: {e['name'].upper()}")


def test_say_silent():
    setup()
    r1 = say("this is output")
    r2 = say("this is output", silent=True)
    assert r1 == r2


def test_indent():
    setup()
    assert say('no indent') == 'no indent'
    assert say('no indent', indent=0) == 'no indent'
    assert say('one indent', indent='1') == '    one indent'
    assert say('one indent', indent='+1') == '    one indent'
    assert say('two indent', indent=2) == '        two indent'
    say.set(indent=1)
    assert say('auto one indent') == '    auto one indent'
    assert say('one plus one indent', indent='+1') == '        one plus one indent'
    assert say('subtract indent', indent='-1') == 'subtract indent'
    assert say('force no indent', indent=0) == 'force no indent'
    say.set(indent=0)
    assert say('no indent again') == 'no indent again'


def test_sep_end():
    setup()
    assert say(1, 2, 3) == '1 2 3'
    assert say(1, 2, 3, sep=',') == '1,2,3'
    assert say(1, 2, 3, sep=', ') == '1, 2, 3'
    say('xyz', end='\n') == 'xyz\n'
    say('xyz', end='\n\n') == 'xyz\n\n'
    say('xyz', end='') == 'xyz'


def test_indent_special():
    setup()
    say.set(indent_str='>>> ')
    assert say('something') == 'something'
    assert say('else', indent=1) == '>>> else'
    assert say('again', indent=2) == '>>> >>> again'
    say.set(indent_str='| ')
    assert say("some text") == 'some text'
    assert say("other", indent="+1") == '| other'


def test_indent_multiline():
    setup()
    assert say('and off\nwe go', indent='+1') == '    and off\n    we go'


def test_with_indent():
    setup()
    with say.settings(indent='+1'):
        assert say("I am indented!") == "    I am indented!"
        with say.settings(indent='+1'):
            assert say("xyz") == "        xyz"
        assert say('one back') == '    one back'
    assert say('back again') == 'back again'

def test_prefix_suffix():
    setup()
    assert say('x', prefix='<', suffix='>') == '<x>'
    assert say('x', end='\n--') == 'x\n--'
    assert say('a\nb\nc', prefix='> ') == '> a\n> b\n> c'
    assert say('a\nb\nc', prefix='> ', suffix='\n') == '> a\n\n> b\n\n> c\n'
    quoter = say.clone(prefix='> ')
    assert quoter('a\nb\nc') == '> a\n> b\n> c'

def test_prefix_in_context_example():
    setup()
    with say.settings(prefix='> '):
        assert say('this') == '> this'
        assert say('that') == '> that'
    assert say('other') == 'other'

def test_colored_output():
    setup()
    with say.settings(prefix='\x1b[34m', suffix='\x1b[0m'):
        assert say('this is blue!') == '\x1b[34mthis is blue!\x1b[0m'
    assert say('not blue') == 'not blue'
    blue = say.clone(prefix='\x1b[34m', suffix='\x1b[0m')
    assert blue('BLUE') == '\x1b[34mBLUE\x1b[0m'

def test_example_3():
    setup()
    items = '1 2 3'.split()

    assert say('TITLE') == 'TITLE'
    for item in items:
        assert say(item, indent=1) == '    ' + str(item)


def test_wrap():
    setup()
    assert say('abc\ndef\nghi', wrap=79) == 'abc def ghi'
    assert say("abcde abcde abcde", wrap=6) == 'abcde\nabcde\nabcde'
    assert say("abcde abcde abcde", wrap=10, indent=1) == '    abcde\n    abcde\n    abcde'

def test_caller_fmt():

    def ucfmt(s):
        return caller_fmt(s).upper()

    x = 12
    y = 'x'

    assert ucfmt("{y!r} is {x}") == "'X' IS 12"

def test_FmtException():

    class Blooper(FmtException, ValueError):
        pass

    x = 12
    try:
        raise Blooper('{x} is cray, yo')
    except ValueError as e:
        assert e.args[0] == '12 is cray, yo'
    except Exception:
        assert False