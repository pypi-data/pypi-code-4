# -*- coding: utf-8 -*-

from logilab.common.testlib import TestCase, unittest_main

from pybill.lib.pdfwriters.utils import escape_text, format_number
from pybill.lib.pdfwriters.utils import TotalizableTable, NumberParagraph
from pybill.lib.pdfwriters import style_normal_left
from reportlab.platypus import Paragraph


class EscapeTextFunctionTest(TestCase):
    def test_no_escaping_characters(self):
        """
        Tests the ``escape_text`` function when the text contains no character
        to be escaped.
        """
        text = "   coucou c'est   moi !    "
        expected_text = "   coucou c'est   moi !    "
        self.assertEqual(expected_text, escape_text(text))

    def test_escaping_characters(self):
        """
        Tests the ``escape_text`` function when the text contains characters
        to be escaped.
        """
        text = "   coucou c'est   moi  & hop <>  !    "
        expected_text = "   coucou c'est   moi  &amp; hop &lt;&gt;  !    "
        self.assertEqual(expected_text, escape_text(text))

    def test_no_escaping_characters_and_normalizing(self):
        """
        Tests the ``escape_text`` function when the text contains no
        character to be escaped and when the normalizing feature is set.
        """
        text = "   coucou c'est   moi !    "
        expected_text = "coucou c'est moi !"
        self.assertEqual(expected_text, escape_text(text, True))

    def test_escaping_characters_and_normalizing(self):
        """
        Tests the ``escape_text`` function when the text contains characters
        to be escaped and when the normalizing feature is set.
        """
        text = "   coucou c'est   moi  & hop <>  !    "
        expected_text = "coucou c'est moi &amp; hop &lt;&gt; !"
        self.assertEqual(expected_text, escape_text(text, True))


class FormatNumberFunctionTest(TestCase):
    def setUp(self):
        """
        Called before each test.
        """
        self.seps = {u'sign': u' ',
                     u'thousands': u' ',
                     u'digits': u','}
        
    def test_number_is_None(self):
        """
        Tests the ``format_number`` function with a number that is None.
        """
        num = None
        expected_text = u""
        self.assertEqual(expected_text, format_number(num, 3, self.seps))

    def test_integer_less_than_thousand(self):
        """
        Tests the ``format_number`` function with an integer less than one
        thousand.
        """
        num = 532
        expected_text = u"532"
        self.assertEqual(expected_text, format_number(num, 0, self.seps))

    def test_integer_less_than_million(self):
        """
        Tests the ``format_number`` function with an integer between one
        thousand and one million.
        """
        num = 47032
        expected_text = u"47 032"
        self.assertEqual(expected_text, format_number(num, 0, self.seps))

    def test_great_integer(self):
        """
        Tests the ``format_number`` function with an integer greater than one
        million.
        """
        num = 2045008
        expected_text = u"2 045 008"
        self.assertEqual(expected_text, format_number(num, 0, self.seps))

    def test_integer_with_digits(self):
        """
        Tests the ``format_number`` function with an integer less than one
        thousand when asking for two digits.
        """
        num = 12345678
        expected_text = u"12 345 678,00"
        self.assertEqual(expected_text, format_number(num,
                                                       separators=self.seps))

    def test_float_rounding_to_lesser(self):
        """
        Tests the ``format_number`` function with a float, especially the
        rounding feature with two digits (case when rounding to lesser).
        """
        num = 532.8845512
        expected_text = u"532,88"
        self.assertEqual(expected_text, format_number(num,
                                                       separators=self.seps))

    def test_float_rounding_middle_to_greater(self):
        """
        Tests the ``format_number`` function with a float, especially the
        rounding feature with two digits (middle case that is rounded to
        greater).
        """
        num = 532.8855512
        expected_text = u"532,89"
        self.assertEqual(expected_text, format_number(num,
                                                       separators=self.seps))

    def test_float_rounding_to_greater(self):
        """
        Tests the ``format_number`` function with a float, especially the
        rounding feature with two digits (case when rounding to greater).
        """
        num = 532.8865512
        expected_text = u"532,89"
        self.assertEqual(expected_text, format_number(num,
                                                       separators=self.seps))

    def test_float_rounding_to_upper_integer(self):
        """
        Tests the ``format_number`` function with a float, especially the
        rounding feature with zero digits (case when rounding to upper integer).
        """
        num = 532.501
        expected_text = u"533"
        self.assertEqual(expected_text, format_number(num, 0, self.seps))

    def test_float_rounding_to_lower_integer(self):
        """
        Tests the ``format_number`` function with a float, especially the
        rounding feature with zero digits (case when rounding to lower integer).
        """
        num = 532.499
        expected_text = u"532"
        self.assertEqual(expected_text, format_number(num, 0, self.seps))

    def test_float_number_of_digits(self):
        """
        Tests the ``format_number`` function with a float, especially the
        number of digits.
        """
        num = 532.88555512
        expected_text = u"532,88556"
        self.assertEqual(expected_text, format_number(num, 5, self.seps))

    def test_great_float(self):
        """
        Tests the ``format_number`` function with an integer greater than one
        million, when four digits are asked
        """
        num = 12345678.123456
        expected_text = u"12 345 678,1235"
        self.assertEqual(expected_text, format_number(num, 4, self.seps))

    def test_negative_number(self):
        """
        Tests the ``format_number`` function with a negative number (float
        number by the way).
        """
        num = -12345678.123456
        expected_text = u"- 12 345 678,1235"
        self.assertEqual(expected_text, format_number(num, 4, self.seps))

    def test_default_separators(self):
        """
        Tests the ``format_number`` function with a negative float number
        when using the default separators for the formatting.
        """
        num = -12345678.123456
        expected_text = u"-12345678.1235"
        self.assertEqual(expected_text, format_number(num, 4))


class TotalizableTableTest(TestCase):
    def setUp(self):
        """
        Called before each test from this class
        """
        table_content = []
        # line 1
        line_content = []
        line_content.append(Paragraph(u"text1.1", style_normal_left))
        line_content.append(Paragraph(u"1", style_normal_left))
        line_content.append(NumberParagraph(1, u"1", style_normal_left))
        table_content.append(line_content)
        # line 2
        line_content = []
        line_content.append(Paragraph(u"text2.1", style_normal_left))
        line_content.append(Paragraph(u"20", style_normal_left))
        line_content.append(NumberParagraph(20.2, u"20", style_normal_left))
        table_content.append(line_content)
        # line 3
        line_content = []
        line_content.append(Paragraph(u"text3.1", style_normal_left))
        line_content.append(Paragraph(u"300", style_normal_left))
        line_content.append(NumberParagraph(300, u"300", style_normal_left))
        table_content.append(line_content)
        # Builds the table
        self.tot_table = TotalizableTable(table_content, [10,10,10], None)
    
    def test_total_computation(self):
        """
        Tests the computation of the total inside a ``TotalizableTable``.
        """
        expected_tot = 321.2
        computed_tot = self.tot_table.compute_total()
        self.assertEqual(expected_tot, computed_tot)


# definitions for automatic unit testing

if __name__ == '__main__':
    unittest_main()
