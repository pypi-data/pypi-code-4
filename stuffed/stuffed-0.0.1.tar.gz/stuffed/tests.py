import unittest
import stuffed
from datetime import datetime

class CreditCardTest(unittest.TestCase):
    def test_one(self):
        c = stuffed.CreditCard.from_swipe("%B4111111111111111^SMITH/JOHN      ^15024041234567891234?\n;4111111111111111=150224041234567891234?")
        self.assertEqual(c.number, "4111111111111111")
        self.assertEqual(c.name, "SMITH/JOHN")
        self.assertEqual(c.track1, "%B4111111111111111^SMITH/JOHN      ^15024041234567891234?")
        self.assertEqual(c.track2, ";4111111111111111=150224041234567891234?")
        self.assertEqual(c.expires, datetime(day=01, month=2, year=2015))
        self.assertIsNone(c.zip)
        self.assertIsNone(c.cvv)

    def test_two(self):
        c = stuffed.CreditCard(number="4111111111111111",
                               expires="feb 2015")
        self.assertEqual(c.number, "4111111111111111")
        self.assertIsNone(c.name)
        self.assertIsNone(c.track1)
        self.assertIsNone(c.track2)
        self.assertEqual(c.expires, datetime(day=01, month=2, year=2015))
        self.assertIsNone(c.zip)
        self.assertIsNone(c.cvv)

if __name__ == '__main__':
    unittest.main()
