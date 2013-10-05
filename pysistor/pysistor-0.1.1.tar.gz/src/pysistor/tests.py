import pysistor
from imp import reload
import unittest

class TestFactory(unittest.TestCase):
    def setUp(self):
        reload(pysistor)

    def test_from_dict(self):
        pysistor.Pysistor.from_dict()

    def test_default(self):
        pysistor.Pysistor.from_dict(set_default=True)
        assert pysistor.Pysistor[None] is not None

    def test_no_expire(self):
        pysistor.Pysistor.from_dict(set_default=True)
        pysistor.Pysistor.store("test", "value")
        assert pysistor.Pysistor.get("test") == "value"
