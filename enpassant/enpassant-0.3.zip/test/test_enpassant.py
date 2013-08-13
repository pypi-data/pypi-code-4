
from enpassant import *

class WrongAnswer(ValueError):
    """
    Raised when test takes wrong fork in a conditional.
    """
    pass

def test_one():
    passer = Passer()
    
    values = [ 1, 0, True, False, "yes", "", [], object() ]
    
    for v in values:
        if passer / v:
            assert bool(passer.value) is True 
            assert passer.value == v
        else:
            assert bool(passer.value) is False 
            assert passer.value == v

def test_unary_value_retrieval():
    passer = Passer()
    
    values = [ 1, 0, True, False, "yes", "", [], object() ]
    
    for v in values:
        if passer / v:
            assert bool(+passer) is True 
            assert +passer == v
        else:
            assert bool(passer.value) is False 
            assert bool(+passer) is False 
            assert +passer == v
            
    class AttrDict(dict):
        """
        Simple attributes-exposed dict class for testing purposes.
        Use stuf, TreeDict, or something better in real apps.
        """
        def __getattr__(self, name):
            return self.__getitem__(name)
        
    d = AttrDict(a=1, b=2, c=lambda x: x * 2)
    if passer / d:
        assert +d.a == 1
        assert +d.b == 2
        assert +d.c(10) == 20
        assert +d['a'] == 1
        assert +d['b'] == 2
        assert +d['c'](10) == 20
    else:
        assert False


def test_alt_operations():
    passer = Passer()
    
    values = [ 1, 0, True, False, "yes", "", [], object() ]
    
    for v in values:
        if passer < v:
            assert bool(passer.value) is True 
            assert passer.value == v
        else:
            assert bool(passer.value) is False 
            assert passer.value == v
            
    for v in values:
        if passer <= v:
            assert bool(passer.value) is True 
            assert passer.value == v
        else:
            assert bool(passer.value) is False 
            assert passer.value == v

def test_call_delivery():
    passer = Passer()
    
    values = [ 1, 0, True, False, "yes", "", [], object() ]

    for v in values:
        if passer <= v:
            assert bool(passer.value) is True 
            assert passer.value == v
        else:
            assert bool(passer.value) is False 
            assert passer.value == v
            
def test_item_forwarding():
    answers = [ 1, 4, 'a']
    result = Passer()
    
    if result / answers:
        assert result[0] == 1
        assert result[1] == 4
        assert result[2] == 'a'
        assert result.value is answers
    else:
        raise WrongAnswer()
        
def test_attribute_forwarding():
    class X(object):
        one = 1
        two = 2
        more = 'more'
        
        def report(self):
            return "{0} is {1} than {2}".format(self.two, self.more, self.one)
        
    result = Passer()
    x = X()
    if result/x:
        assert result.one == 1
        assert result.two == 2
        assert result.more == 'more'
        assert result.value is x
        assert result.report() == '2 is more than 1'
    else:
        raise WrongAnswer()
    
def test_item_setting():
    answers = [ 1, 4, 'a']
    result = Passer()
    
    if result / answers:
        result[2] = 'two'
        result.append('extra')
        assert result[0] == 1
        assert result[1] == 4
        assert result[2] == 'two'
        assert result[3] == 'extra'
        assert len(result.value) == 4
        assert result.value is answers
    else:
        raise WrongAnswer()
    
def test_attribute_setting():
    class X(object):
        one = 1
        two = 2
        more = 'more'
        
        def report(self):
            return "{0} is {1} than {2}".format(self.two, self.more, self.one)
        
    result = Passer()
    x = X()
    if result/x:
        result.one = 'one'
        result.two = 'two'
        assert result.one == 'one'
        assert result.two == 'two'
        assert result.more == 'more'
        assert result.value is x
        assert result.report() == 'two is more than one'
    else:
        raise WrongAnswer()
    
def test_repr():
    values = [ 1, 0, True, False, "yes", "", [] ]
    passer = Passer()
    
    for v in values:
        if passer / v:
            pass
        assert repr(passer) == 'Passer(' + repr(v) + ')'

    
def test_grabber():
    info = Grabber()
    
    if info.name("roger"):
        assert info.name == 'roger'
    if info.empty([]):
        assert False
    else:
        assert info.empty == []
