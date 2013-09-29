import unittest2 as unittest

from gingerit import GingerIt


class TestGingerIt(unittest.TestCase):
    def test(self):
        text = 'The smelt of fliwers bring back memories.'

        parser = GingerIt()
        output = parser.parse(text)
        self.assertEqual(output.get("result"), "The smell of flowers brings back memories")

if __name__ == '__main__':
    unittest.main()
