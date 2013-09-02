from nose.tools import *
from .. import gb

def test_letter_grade():
	calculate = gb.Calculate(73)
	assert_equal(calculate.letter_grade(73), "C")
	
def test_gpa():
	calculate = gb.Calculate(87)
	assert_equal(calculate.course_gpa(87), 3.30)
