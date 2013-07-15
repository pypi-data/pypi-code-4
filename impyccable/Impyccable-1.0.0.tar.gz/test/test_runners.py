from unittest import TestCase
from impyccable.generators import Value
from impyccable.runners import Impyccable, Runner



class GeneratorTests(TestCase):
    def execute(self, value):
        self.assertEqual(value, 10)

    @Impyccable()
    def test_Runner(self):
        run = Runner(self.execute, Value(10))
        run()
