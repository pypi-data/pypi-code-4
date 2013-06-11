from django.test import TestCase

from .enums import ExamStatus
from .models import Exam

class ExamTestCase(TestCase):
    def setUp(self):
        self.exam = Exam.objects.create()

    def test_exam_default(self):
        """ See that it has the default value """
        self.assertEqual(self.exam.status, ExamStatus.DEFAULT)

    def test_status_equals_fail(self):
        self.assertEqual(self.exam.status, ExamStatus.FAIL)

    def test_status_is_not_pass(self):
        self.assertFalse(self.exam.has_passed())

    def test_status_is_pass(self):
        self.exam.passed()
        self.assertEqual(self.exam.status, ExamStatus.PASS)


class EnumTestCase(TestCase):
    def setUp(self):
        self.enum = ExamStatus()

    def test_length(self):
        self.assertEqual(len(self.enum.choicify()), 2)

    def test_choicify(self):
        self.assertEqual(self.enum.choicify(), [(0, 'Fail'), (1, 'Pass')])

    def test_choicify_fail(self):
        self.assertNotEqual(self.enum.choicify(), [(1, 'Pass'), (0, 'Fail')])

    def test_fail_in_key(self):
        self.assertTrue(self.enum.is_in_keys('FAIL'))

    def test_default_in_key(self):
        self.assertFalse(self.enum.is_in_keys('DEFAULT'))

    def test_zero_in_value(self):
        self.assertTrue(self.enum.is_in_values(0))