from unittest import TestCase
from di.decorator import service, inject

@service('a')
class A(object): pass

@inject(['a'])
def partial(a, b):
    return b

class TestPartialInjection(TestCase):
    def test_injected_function_takes_argument_properly(self):
        self.assertEqual('b', partial('b'))