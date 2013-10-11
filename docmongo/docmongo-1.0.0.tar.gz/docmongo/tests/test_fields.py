import unittest
import pytest


class Test_StringField(unittest.TestCase):
    def _makeOne(self, s=None):
        from docmongo import StringField
        return StringField(s)

    def test_type(self):
        obj = self._makeOne("test")
        assert(obj.validate() == True)

        obj = self._makeOne(100)
        with pytest.raises(TypeError):
            obj.validate()

        obj = self._makeOne()
        assert(obj.validate() == True)


class Test_IntField(unittest.TestCase):
    def _makeOne(self, s=None):
        from docmongo import IntField
        return IntField(s)

    def test_type(self):
        obj = self._makeOne(1000)
        assert(obj.validate() == True)

        obj = self._makeOne("100")
        with pytest.raises(TypeError):
            obj.validate()

        obj = self._makeOne()
        assert(obj.validate() == True)


class Test_DictField(unittest.TestCase):
    def _makeOne(self, s=None):
        from docmongo import DictField
        return DictField(s)

    def test_type(self):
        obj = self._makeOne(dict())
        assert(obj.validate() == True)

        obj = self._makeOne(dict(
            a = 100,
            b = "testtest",
            c = 1000
            ))
        assert(obj.validate() == True)

        obj = self._makeOne("100")
        with pytest.raises(TypeError):
            obj.validate()

        obj = self._makeOne()
        assert(obj.validate() == True)

    def test_operation(self):
        obj = self._makeOne()
        obj['test'] = 100
        assert(obj['test'] == 100)
        assert(obj.get('test') == 100)

        obj.update({'hoge': 10000})
        assert(obj.get('hoge') == 10000)
        assert(len(obj) == 2)
        assert('hoge' in obj)
        assert('hogehoge' not in obj)

        obj += {'testga': 'aabb'}
        assert('testga' in obj)
        assert(obj['testga'] == 'aabb')

        for key in obj:
            assert key in ['test', 'hoge', 'testga']


class Test_ListField(unittest.TestCase):
    def _makeOne(self, s=None):
        from docmongo import ListField
        return ListField(s)

    def test_type(self):
        obj = self._makeOne(list())
        assert(obj.validate() == True)

        obj = self._makeOne(["a", 1000, list()])
        assert(obj.validate() == True)

        obj = self._makeOne("100")
        with pytest.raises(TypeError):
            obj.validate()

        obj = self._makeOne()
        assert(obj.validate() == True)

        obj = self._makeOne([1])
        assert(obj[0] == 1)
        obj[0] = 5
        assert(obj[0] == 5)

    def test_operation(self):
        obj = self._makeOne(list())
        obj.append(10)

        assert(obj[0] == 10)
        assert(len(obj) == 1)
        assert(10 in obj)
        assert(1000 not in obj)

        obj += 100
        assert(obj[1] == 100)
        assert(len(obj) == 2)

        for key in obj:
            assert key in [100, 10]


class Test_DateField(unittest.TestCase):
    def _makeOne(self, s=None):
        from docmongo import DateField
        return DateField(s)

    def test_type(self):
        import datetime
        obj = self._makeOne(datetime.datetime.now())
        assert(obj.validate() == True)

        obj = self._makeOne("100")
        with pytest.raises(TypeError):
            obj.validate()

        obj = self._makeOne(100)
        with pytest.raises(TypeError):
            obj.validate()

        obj = self._makeOne()
        assert(obj.validate() == True)
