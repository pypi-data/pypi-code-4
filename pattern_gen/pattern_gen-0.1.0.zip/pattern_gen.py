"""This is pattern.py module which provides pattern1(), pattern2(), pattern3()
functions to print 3 basic patterns with given character."""


def pattern1(c):
    """Prints Pattern of Type 1"""
    for i in range(0,5):
        print(c*5)

def pattern2(c):
    """Prints Pattern of Type 2"""
    for i in range(1,6):
        print(c*i)

def pattern3(c):
    """Prints Pattern of Type 3"""
    for i in range(1,6):
        print(c*(6-i))

