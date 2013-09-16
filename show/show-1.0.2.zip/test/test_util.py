from show.util import *

def test_omitnames():
    """
    Make sure the basic omission helper works
    """

    def qw(data):
        """
        Quote words. Thanks, Perl!
        """
        return data.split() if isinstance(data, str) else data

    def check_list(lst, tests):
        lst = qw(lst)
        for pat, answer in tests.items():
            answer = qw(answer)
            assert omitnames(lst, pat, sort=False) == answer
            assert omitnames(lst, pat, sort=True) == sorted(answer)
            assert omitnames(lst, pat) == sorted(answer)

    L1 = 'one two three four five six seven'
    L1_tests = {
        'one': 'two three four five six seven',
        't*':  'one four five six seven',
        't* s*': 'one four five',
        't* f* s*': 'one',
        '*o*':  'three five six seven',
        '*': []
    }

    check_list(L1, L1_tests)

    L2 = '_this __that something_else _and __or__'
    L2_tests = {
        'one': L2,
        '_*': 'something_else',
        '__*': '_this something_else _and',
        '*_': '_this __that something_else _and',
        'and': L2,
        '*and': '_this __that something_else __or__'
    }

    check_list(L2, L2_tests)

def test_typename_basic():
    assert typename(4) == '<int>'
    assert typename(4.5) == '<float>'
    assert typename(5+7j) == '<complex>'
    assert typename([]) == '<list>'
    assert typename({}) == '<dict>'
    assert typename(set()) == '<set>'

def test_typename_classes():

    class R(object): pass
    r = R()

    assert typename(R) == '<type>'
    assert typename(r) == '<R>'

    def nested():
        class RR(object): pass
        assert typename(RR) == '<type>'
        r2 = RR()
        assert typename(r2) == '<RR>'

    nested()

def test_lambda_eval():

    noncallables  = [4, 4.5, 5+7j, [], {}, set()]
    for nc in noncallables:
        assert lambda_eval(nc) == nc

    x = 12
    assert lambda_eval(x) == x
    assert lambda_eval(lambda: x) == x
    assert lambda_eval(lambda: x < 10) == False
    assert lambda_eval(lambda: x > 10) == True
