# -*- coding: utf-8 -*-
"""
    Test Nereid Review

    :copyright: (c) 2013 by Openlabs Technologies & Consulting (P) Limited
    :license: BSD, see LICENSE for more details.
"""
import unittest

import trytond.tests.test_tryton
from trytond.tests.test_tryton import POOL, USER, DB_NAME, CONTEXT, \
    test_view, test_depends
from nereid.testing import NereidTestCase
from trytond.transaction import Transaction
from trytond.exceptions import UserError


class TestNereidReview(NereidTestCase):
    "Test Nereid Review"

    def setUp(self):
        "Setup"
        trytond.tests.test_tryton.install_module('nereid_review')

        self.Party = POOL.get('party.party')
        self.Company = POOL.get('company.company')
        self.Currency = POOL.get('currency.currency')
        self.NereidUser = POOL.get('nereid.user')
        self.NereidReview = POOL.get('nereid.review')

    def test_0005_test_view(self):
        """
        Test the view
        """
        test_view('nereid_review')

    def test_0006_test_depends(self):
        """
        Test Depends
        """
        test_depends()

    def test_0010_test_valid_rating_constraint(self):
        """
        Check valid rating constraint.
        """
        with Transaction().start(DB_NAME, USER, CONTEXT):
            usd, = self.Currency.create([{
                'name': 'US Dollar',
                'code': 'USD',
                'symbol': '$',
            }])
            self.company, = self.Company.create([{
                'party': self.Party.create([{'name': 'Openlabs'}])[0].id,
                'currency': usd.id
            }])

            nereid_user_party, = self.Party.create([{
                'name': 'Guest User',
            }])
            nereid_user, = self.NereidUser.create([{
                'party': nereid_user_party.id,
                'display_name': 'Guest User',
                'email': 'guest@openlabs.co.in',
                'password': 'password',
                'company': self.company.id,
            }])

            # Create review between rating of 1-5
            review1, = self.NereidReview.create([{
                'title': 'Review-1',
                'rating': 4,
                'comment': 'good',
                'nereid_user': nereid_user.id,
            }])
            self.assert_(review1)

            # Create review with empty rating
            review2, = self.NereidReview.create([{
                'title': 'Review-2',
                'comment': 'rating need to be added',
                'nereid_user': nereid_user.id,
            }])
            self.assert_(review2)

            # Try to create reviw with rating out of scale
            self.assertRaises(
                UserError, self.NereidReview.create, [{
                    'title': 'Review-1',
                    'rating': 10,
                    'comment': 'Rating is not in scale',
                    'nereid_user': nereid_user.id,
                }],
            )


def suite():
    "Define test suite"
    suite = unittest.TestSuite()
    suite.addTests(
        unittest.TestLoader().loadTestsFromTestCase(TestNereidReview)
    )
    return suite


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
