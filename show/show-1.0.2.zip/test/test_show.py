
import pytest
from show import Show, NoShow, noshow
import sys
import platform
import six

_PY3 = sys.version_info[0] == 3
_PYPY = platform.python_implementation() == 'PyPy'

show = Show(where=False, retvalue=True)

global_var = 'hey!'

def nospaces(s):
    return s.replace(' ', '')

def test_basic(param = 'Yo'):

    a = 1
    b = 3.141
    c = "something else!"

    assert show(a) == 'a: 1'
    assert show(a, b) == 'a: 1  b: 3.141'
    assert show(a, b, c) == "a: 1  b: 3.141  c: 'something else!'"

    assert show(len(c), c) == \
                "len(c): 15  c: 'something else!'"

            # anything with paraens in it must be on separate line, given weak parser
            # of show parameters

def test_literals():
    assert show(1 + 1) == '1 + 1: 2'
    assert show(1+1) == '1 + 1: 2'

    # for when using astor as codegen replacement
    # assert show(1 + 1) == '(1 + 1): 2'
    # assert show(1+1) == '(1 + 1): 2'

    # NB output may have more or fewer spaces than actual parameter, based on codegen.to_source()
    # creating its 'idealized' code output

    # when we were using codegen to recreate source, it did so without parenthesis
    # astor uses parens -- which seem superflous here...but printing literals isn't
    # the main use case, so whatever...

def test_say_params():
    a = 1
    b = 3.141
    c = "something else!"

    assert show(a, indent='+1') == '    a: 1'
    assert show(a, b, sep='\n') == 'a: 1\nb: 3.141'

def test_strings():
    assert show('this') == "this"
    x = 44
    assert show("x = {x}") == 'x = 44'

def test_string_example():

    n = 14312
    assert show("{n} iterations, still running") == "14312 iterations, still running"

    s = '{n} iterations'
    assert show(s) == "s: '{n} iterations'"

def test_set():

    s = set([1,2,99])

    # native literals for sets different in py2 and py3
    if _PY3:
        assert show(s) == "s: {1, 2, 99}"
    else:
        assert show(s) == "s: set([1, 2, 99])"

def test_show_example():

    x = 12
    nums = list(range(4))

    assert show(x) == 'x: 12'
    assert show(nums) == 'nums: [0, 1, 2, 3]'
    assert show(x, nums, len(nums)) == \
        'x: 12  nums: [0, 1, 2, 3]  len(nums): 4'
    assert show(x, nums, len(nums), indent='+1') == \
        '    x: 12  nums: [0, 1, 2, 3]  len(nums): 4'
    assert show(x, nums, len(nums), sep='\n') == \
        'x: 12\nnums: [0, 1, 2, 3]\nlen(nums): 4'
    assert show(x, nums, len(nums), sep='\n', indent=1) == \
        '    x: 12\n    nums: [0, 1, 2, 3]\n    len(nums): 4'

def test_show_items():
    nums = list(range(4))
    assert show.items(nums) == \
        'nums (4 items): [0, 1, 2, 3]'

    astring = 'this'
    assert show.items(astring) == \
        "astring (4 chars): 'this'"

    d = {'a': 1, 'b': 2}
    fstr =  show.items(d)
    assert fstr == "d (2 items): {'a': 1, 'b': 2}" or fstr == "d (2 items): {'b': 2, 'a': 1}"


def test_show_dir():

    class R(object):
        x = 4
        def __init__(self):
            self.y = 44
            self._other = 943
    r = R()

    assert show.dir(r) == "r<R>: _other x y"

    if _PY3:
        full_ans = 'r<R>: __class__ __delattr__ __dict__ __dir__ __doc__ __eq__ __format__ __ge__ __getattribute__ __gt__ __hash__ __init__ __le__ __lt__ __module__ __ne__ __new__ __reduce__ __reduce_ex__ __repr__ __setattr__ __sizeof__ __str__ __subclasshook__ __weakref__ _other x y'
    elif _PYPY:
        full_ans = 'r<R>: __class__ __delattr__ __dict__ __doc__ __format__ __getattribute__ __hash__ __init__ __module__ __new__ __reduce__ __reduce_ex__ __repr__ __setattr__ __str__ __subclasshook__ __weakref__ _other x y'
    else:
        full_ans = 'r<R>: __class__ __delattr__ __dict__ __doc__ __format__ __getattribute__ __hash__ __init__ __module__ __new__ __reduce__ __reduce_ex__ __repr__ __setattr__ __sizeof__ __str__ __subclasshook__ __weakref__ _other x y'


    tests = {
        '_*':  "r<R>: x y",
        '__*': "r<R>: _other x y",
        '':    full_ans,
        None:  full_ans,
    }

    for pat, answer in tests.items():
        assert show.dir(r, omit=pat) == answer

def test_show_props():

    class O(object):
        name    = None
        age     = None
        address = None
    o = O()
    o.name = 'An Object'
    o.age  = 2
    o.address = 'RAM'
    #assert show.props(o) == "o (O): address='RAM' age=2 name='An Object'"
    #assert show.props(o, 'name,age,address') == "o (O): name='An Object' age=2 address='RAM'"
    #assert show.props(o, 'name,age') == "o (O): name='An Object' age=2"
    assert show.props(o) == "o<O>:\n    address='RAM'\n    age=2\n    name='An Object'"
    assert show.props(o, 'name,age,address') == "o<O>:\n    name='An Object'\n    age=2\n    address='RAM'"
    assert show.props(o, 'name,age') == "o<O>:\n    name='An Object'\n    age=2"

    assert show.props(o, 'name,age') == show(o, props='name,age')

    # Other, not (yet, at any rate) API options

    # v0 = show.props(o)
    # assert show(props(o)) == v0

    # v1 = show.props(o, 'name,age')
    # assert show(props(o, 'name,age')) == v1

def test_show_props2():

    class OO(object):
        def __init__(self, name, age, address):
            self.name = name
            self._name = name.upper()
            self.age  = age
            self.address = address
        def test(self):
            return self.age > 17
        def best(self):
            return self.name.capitalize()

    oo = OO('Joe', 36, 'Waverly Place')

    assert show.props(oo) == "oo<OO>:\n    address='Waverly Place'\n    age=36\n    name='Joe'\n    _name='JOE'"

def test_show_real_properties():

    class P(object):
        def __init__(self, name):
            self._name = name.upper()
            self.name = name
        @property
        def namer(self):
            return self._name.lower()
        def named(self):
            return self.name

    p = P('Joe')
    assert show.props(p) == "p<P>:\n    name='Joe'\n    namer='joe'\n    _name='JOE'"

def test_show_locals():
    x = 1
    y = 2
    assert show.locals() == 'x: 1  y: 2'

    a = 22
    b = 23
    assert show.locals(omit='x') == 'a: 22  b: 23  y: 2'
    # assert show.locals(global_var) == "global_var: 'hey!'  x: 1  y: 2"

def test_show_changed():
    x = 1
    assert show.changed() == 'x: 1'
    y = 2
    assert show.changed() == 'y: 2'
    x = 4
    assert show.changed() == 'x: 4'
    x = 5
    y = 3
    # _z = 99

    changed = show.changed()
    assert changed == 'x: 5  y: 3' or changed == 'y: 3  x: 5'

    # assert show.changed() == six.u('\u2205')

    # assert show.changed(_z) == '_z: 99'
    # assert show.changed() == six.u('\u2205')

def test_show_flag():
    """
    Test that the show keyword argument actually turns showing on or off.
    """
    x = 1

    # NB the retvalue setting is set to same as the show attribute because
    # here in this testing situation, we're testing the return not the pure
    # output


    # Test instance on-off
    assert show(x) == 'x: 1'
    assert show(x, show=True, retvalue=True) == 'x: 1'
    assert show(x, show=False, retvalue=False) == None

    # Now test global on-off settings, and instance overrides

    show.set(show=False, retvalue=False)
    assert show(x) == None
    assert show(x, show=True, retvalue=True) == 'x: 1'
    show.set(show=True, retvalue=True)
    assert show(x) == 'x: 1'
    assert show(x, show=False, retvalue=False) == None

    # Now test that clones are independently controllable
    show_verbose = show.clone()
    show(show_verbose.options)
    assert show(x * 5) == 'x * 5: 5'
    assert show_verbose(x * 5) == 'x * 5: 5'

    show_verbose.set(show=False, retvalue=False)
    assert show(x * 6) == 'x * 6: 6'
    assert show_verbose(x * 6) == None
    show.set(show=False, retvalue=False)
    assert show(x * 7) == None
    assert show_verbose(x * 7) == None
    show.set(show=True, retvalue=True)
    assert show(x * 8) == 'x * 8: 8'
    assert show_verbose(x * 8) == None
    show_verbose.set(show=True, retvalue=True)
    assert show(x * 9) == 'x * 9: 9'
    assert show_verbose(x * 9) == 'x * 9: 9'

    # Now test lambda expressions for showing
    debug = True
    assert show(x * 5) == 'x * 5: 5'
    show.set(show=lambda: debug)
    show.props(show.options, omit='_*')
    assert show.options.show() == debug
    assert debug == True
    assert show(x * 5) == 'x * 5: 5'
    debug = False
    assert show(x * 5) == None

    # clean up for rest of testing
    debug = True
    show.set(show=True)


def test_show_retval(capsys):

    show = Show(where=False, retvalue=True)

    # this tweak needed to make pytest's capsys work right
    show.say.options.files = [sys.stdout]

    @show.retval
    def f(a):
        return a + 1

    assert f(12) == 13
    out, err = capsys.readouterr()
    assert out == "f(a=12) -> 13\n"
    assert err == ""

# Does not test interactive usage (under ipython, eg) in any automated fashion.
# Nor does it test the formatted output through Pygments and pformat.

def test_noshow(capsys):
    show = Show(where=False, retvalue=True)
    show = noshow

    out, err = capsys.readouterr()
    assert show('this') is None
    assert out == ""
    assert err == ""
