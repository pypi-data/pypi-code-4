"""
CADD Stat tests
"""

from django.core import mail
from django.core.urlresolvers import reverse
from django.test import Client, TestCase

from .forms import FeedbackForm
from .tasks import (task_cohen, task_friedman, task_cohen_kappa, task_mad, task_mannwhitneyu, task_pearson,
                    task_paired_t, task_tau)
import settings as caddstat_settings


class StatisticsTest(TestCase):

    def setUp(self):
        self.dataOne = [4.5, 9.4, 0.6]
        self.dataTwo = [8.5, 6.4, 6.6]
        self.dataThree = [4.7, 7.4, 7.2]
        self.dataOneCat = [1, 4, 7, 4]
        self.dataTwoCat = [4, 7, 9, 9]

    def test_effectsize(self):

        cohensd = task_cohen(self.dataOne, self.dataTwo)
        self.assertEqual(0.8864, cohensd)

    def test_friedman(self):

        chi, pvalue = task_friedman(self.dataOne, self.dataTwo, self.dataThree)
        self.assertEqual(0.6666666666666643, chi)
        self.assertEqual(0.71653131057379005, pvalue)

    def test_kappa(self):

        kappa_output = """    Simple Kappa Coefficient
--------------------------------
Kappa       -0.2308
ASE         0.0947
95% Lower Conf Limit      -0.4163
95% Upper Conf Limit      -0.0452

   Test of H0: Simple Kappa = 0

ASE under H00.1923
Z           -1.2000
One-sided Pr >  Z         0.8849
Two-sided Pr > |Z|        0.2301
"""

        kappa = task_cohen_kappa(self.dataOneCat, self.dataTwoCat)
        self.assertEqual(kappa_output, kappa)

    def test_mad(self):

        mad = task_mad(self.dataOne)
        self.assertEqual(5.7821486521718475, mad)

    def test_mannwhiney(self):

        uvalue, pvalue = task_mannwhitneyu(self.dataOne, self.dataTwo)
        self.assertEqual(3.0, uvalue)
        self.assertEqual(0.33126029177002869, pvalue)

    def test_pearson(self):

        rvalue, pvalue = task_pearson(self.dataOne, self.dataTwo)
        self.assertEqual(-0.15131761015151463, rvalue)
        self.assertEqual(0.90329675876735349, pvalue)

    def test_paired_t(self):

        tvalue, pvalue = task_paired_t(self.dataOne, self.dataTwo)
        self.assertEqual(-0.8551861104941366, tvalue)
        self.assertEqual(0.48254511033179903, pvalue)

    def test_tau(self):

        tau, pvalue = task_tau(self.dataOne, self.dataTwo)
        self.assertEqual(-0.33333333333333326, tau)
        self.assertEqual(0.60150814411369402, pvalue)


class FeedbackTest(TestCase):
    """
    Send us some feedback
    """

    def setUp(self):
        self.client = Client()

    def test_feedback_form(self):
        """
        Test FeedbackForm only
        """

        correct_form_data = {
            'name': 'Joe Example',
            'email': 'joe@example.com',
            'message': 'feedback',
        }
        form = FeedbackForm(data=correct_form_data)
        self.assertTrue(form.is_valid())

        incorrect_form_data = {
            'name': 'Joe Example',
            'email': 'joeexample',
            'message': 'feedback',
        }
        form = FeedbackForm(data=incorrect_form_data)
        self.assertFalse(form.is_valid())

    def test_feedback_view(self):
        """
        Test the full view, including email
        """

        form_data = {
            'name': 'Joe Example',
            'email': 'joe@example.com',
            'message': 'feedback',
        }

        response = self.client.post(reverse('caddstat.views.feedback'), form_data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.templates[0].name, 'caddstat/emails/feedback.txt')
        self.assertEqual(response.templates[1].name, 'caddstat/feedbackthanks.html')

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'CADD Stat feedback from {0}'.format(form_data['name']))
        self.assertEqual(mail.outbox[0].to, [caddstat_settings.CADDSTAT_FEEDBACK_EMAIL])
        self.assertEqual(mail.outbox[0].from_email, form_data['email'])