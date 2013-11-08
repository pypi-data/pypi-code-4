import unittest
from datetime import timedelta, datetime
from derptime import WorkingHoursDateTime

class SubtractOtherDatetimeTests(unittest.TestCase):
    def test_regular_positive(self):
        whdt1 = WorkingHoursDateTime(2013,11,5,10,10,10,666)
        whdt2 = WorkingHoursDateTime(2013,11,5,11,10,10,666)
        expected =  timedelta(days=0, seconds=3600, microseconds=0)

        self.failUnlessEqual(whdt2 - whdt1, expected)

    def test_weekend_positive(self):
        whdt1 = WorkingHoursDateTime(2013,11,8,10,10,10,666)
        whdt2 = WorkingHoursDateTime(2013,11,11,11,10,10,666)
        expected =  timedelta(days=1, seconds=3600, microseconds=0)

        self.failUnlessEqual(whdt2 - whdt1, expected)

    def test_regular_negative(self):
        whdt1 = WorkingHoursDateTime(2013,11,5,10,10,10,666)
        whdt2 = WorkingHoursDateTime(2013,11,5,11,10,10,666)
        expected =  timedelta(days=-1, seconds=23*3600, microseconds=0)

        self.failUnlessEqual(whdt1 - whdt2, expected)
    

class AddTimedeltaTests(unittest.TestCase):

    def test_regular(self):
        whdt = WorkingHoursDateTime(2013,11,6,11,11,11,111)
        d = timedelta(days=1, seconds=3600 + 60 + 1, microseconds=1)
        expected =  WorkingHoursDateTime(2013,11,7,12,12,12,112)
        
        self.failUnlessEqual(whdt + d, expected)


    def test_over_weekend(self):
        whdt = WorkingHoursDateTime(2013,11,8,10,11,12,345)
        d = timedelta(days=1, seconds=3665, microseconds=111)
        expected = WorkingHoursDateTime(2013,11,11,11,12,17,456)
        
        self.failUnlessEqual(whdt + d, expected)


    def test_weekend_edge1(self):
        whdt = WorkingHoursDateTime(2013,11,9,0,0,0,0)
        d = timedelta(days=0, seconds=3666, microseconds=111)
        expected = WorkingHoursDateTime(2013,11,11,1,1,6,111)

        self.failUnlessEqual(whdt + d, expected)


    def test_weekend_edge2(self):
        whdt = WorkingHoursDateTime(2013,11,8,10,10,10,500000)
        d = timedelta(days=0, seconds=13*3600 + 49*60 + 49, microseconds=500000)
        expected = WorkingHoursDateTime(2013,11,11,0,0,0,0)

        self.failUnlessEqual(whdt + d, expected)


    def test_multipl_weekends(self):
        whdt = WorkingHoursDateTime(2013,11,6,10,11,12,13)
        d = timedelta(days=10, seconds=3600 + 60 + 1, microseconds=1)
        expected = WorkingHoursDateTime(2013,11,20,11,12,13,14)

        self.failUnlessEqual(whdt + d, expected)


    def test_from_weekend(self):
        whdt = WorkingHoursDateTime(2013,11,9,10,11,12,345)
        d = timedelta(days=0, seconds=3600 + 60 + 1, microseconds=111)
        expected = WorkingHoursDateTime(2013,11,11,1,1,1,111)

        self.failUnlessEqual(whdt + d, expected)



class SubtractTimedeltaTests(unittest.TestCase):
    
    def test_regular(self):
        whdt = WorkingHoursDateTime(2013,11,8,10,10,10,666)
        d = timedelta(days=3, seconds=3665, microseconds=300)
        expected = WorkingHoursDateTime(2013,11,5,9,9,5,366)

        self.failUnlessEqual(whdt - d, expected)


    def test_over_weekend(self):
        whdt = WorkingHoursDateTime(2013,11,11,  10,11,12,  345)
        d = timedelta(days=1, seconds=3665, microseconds=111)
        expected = WorkingHoursDateTime(2013,11,8,  9,10,7,  234)
        
        self.failUnlessEqual(whdt - d, expected)


    def test_weekend_edge1(self):
        whdt = WorkingHoursDateTime(2013,11,11, 1,1,6, 111)
        d = timedelta(days=0, seconds=3600 + 60 + 6, microseconds=111)
        expected = WorkingHoursDateTime(2013,11,11,0,0,0,0)

        self.failUnlessEqual(whdt - d, expected)


    def test_weekend_edge2(self):
        whdt = WorkingHoursDateTime(2013,11,11, 0,0,0,  0000)
        d = timedelta(days=0, seconds=3600 + 60 + 6, microseconds=1)
        expected = WorkingHoursDateTime(2013,11,8, 22,58,53 ,999999)

        self.failUnlessEqual(whdt - d, expected)


    def test_multipl_weekends(self):
        whdt = WorkingHoursDateTime(2013,11,20,11,12,13,14)
        d = timedelta(days=10, seconds=3600 + 60 + 1, microseconds=1)
        expected = WorkingHoursDateTime(2013,11,6,10,11,12,13)

        self.failUnlessEqual(whdt - d, expected)


    def test_from_weekend(self):
        whdt = WorkingHoursDateTime(2013,11,9,10,11,12,345)
        d = timedelta(days=0, seconds=3600 + 60 + 1, microseconds=1)
        expected = WorkingHoursDateTime(2013,11,8,22,58,58,999999)

        self.failUnlessEqual(whdt - d, expected)



def main():
    unittest.main()

if __name__ == '__main__':
    main()

