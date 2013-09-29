import unittest


class Foo(object):
    def _priv(self):
        pass


class BasicTest(unittest.TestCase):
    pass

    #def test_timeout(self):
       # pylint: disable-msg=W0212
    #    self.assertRaises(Timeout, helpers._request, self.r,
    #                      self.r.config['comments'], timeout=0.001)

    def fail_test(self):
        foo_instance = Foo()
        foo_instance._priv()


class EmbedTextTest(unittest.TestCase):
    def fail_test(self):
        foo_instance = Foo()
        foo_instance._priv()

if __name__ == '__main__':
    unittest.main()
