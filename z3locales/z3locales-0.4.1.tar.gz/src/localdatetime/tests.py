# -*- coding: utf-8 -*-
# Copyright (c) 2012  Infrae. All rights reserved.
# See also LICENSE.txt
import unittest
import localdatetime
from DateTime import DateTime
from datetime import datetime


class LocalTimeTestCase(unittest.TestCase):

    def test_get_formatted_date_datetime(self):
        # Test some dates from different locales
        dt = datetime(2005, 02, 01, 19, 13)

        fd = localdatetime.get_formatted_date(
            dt, size="short", locale="nl")
        self.assertEquals(u'1-2-05 19:13', fd)

        fd = localdatetime.get_formatted_date(
            dt, size="medium", locale="nl")
        self.assertEquals(u'1-feb-2005 19:13:00', fd)

        fd = localdatetime.get_formatted_date(
            dt, size="long", locale="nl")
        self.assertEquals(u'1 februari 2005 19:13:00 +000', fd)

    def test_get_formatted_date_invalid_locale(self):
        """If the local is invalid, it should fallback to english.
        """
        dt = datetime(2005, 02, 01, 19, 13)

        # Test invalid local
        fd = localdatetime.get_formatted_date(
            dt, size="long", locale="u1")
        self.assertEquals(u'February 1, 2005 7:13:00 PM +000', fd)

    def test_get_formatted_date_tuple(self):
        # test some dates from different locales
        dt = [int(p) for p in DateTime('2005-02-01 19:13').parts()[:6]]

        fd = localdatetime.get_formatted_date(
            dt, size="short", locale="nl")
        self.assertEquals(u'1-2-05 19:13', fd)

        fd = localdatetime.get_formatted_date(
            dt, size="medium", locale="nl")
        self.assertEquals(u'1-feb-2005 19:13:00', fd)

        fd = localdatetime.get_formatted_date(
            dt, size="long", locale="nl")
        self.assertEquals(u'1 februari 2005 19:13:00 +000', fd)

        fd = localdatetime.get_formatted_date(
            dt, size="full", locale="nl")
        self.assertEquals(u'dinsdag 1 februari 2005 19:13:00 uur +000', fd)

        fd = localdatetime.get_formatted_date(
            dt, size="short", locale="en")
        self.assertEquals(u'2/1/05 7:13 PM', fd)

        fd = localdatetime.get_formatted_date(
            dt, size="short", locale="en-za")
        self.assertEquals(u'2005/02/01 7:13 PM', fd)

    def test_month_utilities(self):
        # test the month names of certain locales
        months = localdatetime.get_month_names(locale='nl')
        self.assertEquals([u'januari', u'februari', u'maart', u'april',
                    u'mei', u'juni', u'juli', u'augustus', u'september',
                    u'oktober', u'november', u'december'], months)

        monthabbrs = localdatetime.get_month_abbreviations(locale='nl')
        self.assertEquals([u'jan', u'feb', u'mrt', u'apr', u'mei', u'jun',
                    u'jul', u'aug', u'sep', u'okt', u'nov', u'dec'],
                    monthabbrs)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(LocalTimeTestCase))
    return suite
