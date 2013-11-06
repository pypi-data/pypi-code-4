import unittest2 as unittest


class TestMonthYearWidget(unittest.TestCase):

    def createInstance(self):
        from plone.formwidget.datetime.at.widget import MonthYearWidget
        return MonthYearWidget()

    def test_subclass(self):
        from plone.formwidget.datetime.at.widget import MonthYearWidget
        from plone.formwidget.datetime.base import AbstractMonthYearWidget
        from plone.formwidget.datetime.at.widget import DateWidget
        self.assertTrue(MonthYearWidget, (AbstractMonthYearWidget, DateWidget))

    def test__properties(self):
        instance = self.createInstance()
        self.assertEqual(
            instance._properties,
            {
                'blurrable': False,
                'condition': '',
                'description': '',
                'first_day': None,
                'helper_css': (),
                'helper_js': (),
                'label': '',
                'macro': 'monthyear_input',
                'modes': ('view', 'edit'),
                'populate': True,
                'postback': True,
                'show_calendar': True,
                'show_content_type': False,
                'visible': {'edit': 'visible', 'view': 'visible'},
                'years_range': (-10, 10),
            }
        )
