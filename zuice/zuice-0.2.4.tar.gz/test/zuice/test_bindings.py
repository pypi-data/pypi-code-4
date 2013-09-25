from nose.tools import assert_raises
from nose.tools import assert_equals

from zuice.bindings import AlreadyBoundException
from zuice.bindings import Bindings

class Apple(object):
    pass

def test_key_in_bindings_if_key_has_been_bound():
    apple = Apple()
    bindings = Bindings()
    bindings.bind("apple").to_instance(apple)
    
    assert "apple" in bindings
    assert "banana" not in bindings

def test_cannot_bind_using_the_same_binder_more_than_once():
    apple = Apple()
    bindings = Bindings()
    binder = bindings.bind(Apple)
    binder.to_provider(lambda injector: apple)
    assert_raises(AlreadyBoundException, lambda: binder.to_provider(lambda injector: apple))

def test_cannot_bind_the_same_key_more_than_once():
    apple = Apple()
    bindings = Bindings()
    bindings.bind('apple').to_instance(apple)
    assert_raises(AlreadyBoundException, lambda: bindings.bind('apple'))
    assert_raises(AlreadyBoundException, lambda: bindings.bind('apple'))

def test_cannot_bind_key_to_itself():
    bindings = Bindings()
    assert_raises(TypeError, lambda: bindings.bind("apple").to_key("apple"))

def test_can_update_bindings_with_more_bindings():
    bindings = Bindings()
    bindings.bind("maximum_threads").to_instance(5)
    
    new_bindings = Bindings()
    new_bindings.bind("minimum_threads").to_instance(2)
    
    bindings.update(new_bindings)
    assert_equals(bindings["maximum_threads"](None), 5)
    assert_equals(bindings["minimum_threads"](None), 2)

def test_cannot_override_existing_bindings():
    bindings = Bindings()
    bindings.bind("maximum_threads").to_instance(5)
    
    new_bindings = Bindings()
    new_bindings.bind("maximum_threads").to_instance(2)
    
    assert_raises(AlreadyBoundException, lambda: bindings.update(new_bindings))
