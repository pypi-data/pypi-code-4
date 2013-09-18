from unittest import TestCase
from di.decorator import service, inject
from di import ServiceStore

class TestDecorators(TestCase):

    def test_function_service_added(self):
        actual = ServiceStore.get_service('sf').__name__
        self.assertEqual('func', actual, "Service not loaded properly.  Expecting: 'func', got: " + actual)

    def test_class_service_added(self):
        actual = ServiceStore.get_service('sc').__class__
        self.assertEqual(klass, actual, "Service not loaded properly.  Expecting: '" + repr(klass) + "', got: '" + repr(actual) + "'")

    def test_inject_works_on_function(self):
        self.assertEqual('me', clone(), "Injection failed.")

    def test_inject_works_on_init(self):
        i = injected()
        actual_class = i.get_k().__class__
        self.assertEqual(klass, actual_class, "Injection failed for class service.")

        actual_func = i.get_f().__name__
        self.assertEqual('func', actual_func, "Injection failed for function service.")

    def test_injected_service_works(self):
        i = ServiceStore.get_service('sn')
        actual_class = i.get_k().__class__
        self.assertEqual(klass, actual_class, "Injection failed for class service.")

        actual_func = i.get_f().__name__
        self.assertEqual('func', actual_func, "Injection failed for function service.")


@service('sf', ns='default')
def func(arg):
    return arg

@service('sc')
class klass(object): pass

@inject(['sf'])
def clone(f):
    return f('me')

class injected(object):
    @inject(['sc','sf'])
    def __init__(self, k, f):
        self.k = k
        self.f = f

    def get_k(self):
        return self.k

    def get_f(self):
        return self.f

@service('sn')
class injected_service(object):
    @inject(['sc','sf'])
    def __init__(self, k, f):
        self.k = k
        self.f = f

    def get_k(self):
        return self.k

    def get_f(self):
        return self.f
