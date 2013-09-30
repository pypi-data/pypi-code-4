all_tests = ['test1', 'test2', 'test3']


def test1(session):
    yield '^d^k^k12345<enter><home><home>^k^p^p^a^k^p^p^a^k^p^p^p^p.<enter>'
    yield '# hello<enter>'
    yield 'A' * 25 * 1#80
    yield '<up>^a^b^b<down>^c<page-up>^p'
    yield 'if 1:<enter>a = 1<enter>b = a'
    yield '<enter>^x^w<bs><bs><bs><bs>self-test.txt<enter>^q' 
test1.args = ['asdf']

def test2(session):
    yield '<home><home>^shello^s <home>^b^b<up>^d'
    yield '^sA<right>^k^x^wa.py<enter>'
    yield '^oself-test.txt<enter>^v2^q' 
test2.args = ['self-test.txt']

def test3(session):
    session.scr.position = (3, 0)
    yield 'a.bc<enter><mouse-clicked>^d'
    assert session.docs[-1].lines[0] == 'abc'
    session.scr.position = (3, 3)
    yield '<mouse-clicked>'
    assert session.docs[-1].view.pos == (0, 1)
    yield '1<enter>2<enter><up><up><up><end><down>'
    assert session.docs[-1].view.pos == (1, 1)
    yield '^q'
