#!/usr/bin/env python
from nose.tools import *
import bioa as b


class TestValidation(object):

    def test_shannon_entropy(self):
        data = {"heads": 0.5, "tails": 0.5}
        expected = 1.0
        actual = b.shannon_entropy(data)
        eq_(expected, actual, "shannon entropy values differ")

        data = {"heads": 1.0, "tails": 0.0}
        expected = 0.0
        actual = b.shannon_entropy(data)
        eq_(expected, actual, "shannon entropy values differ")

    def test_jensen_shannon_divergence(self):
        data = {"heads": 0.5, "tails": 0.5}
        datapred = {"heads": 0.5, "tails": 0.5}
        expected = 0.0
        actual = b.jensen_shannon_divergence(data, datapred)
        eq_(expected, actual, "jensen-shannon divergence values differ")

        data = {"heads": 0.5, "tails": 0.5}
        datapred = {"heads": 1.0, "tails": 0.0}
        expected = 0.3112781244591328
        actual = b.jensen_shannon_divergence(data, datapred)
        eq_(expected, actual, "jensen-shannon divergence values differ")

    def test_kullback_leibler_divergence(self):
        data = {"heads": 0.5, "tails": 0.5}
        datapred = {"heads": 0.5, "tails": 0.5}
        expected = 0.0
        actual = b.kullback_leibler_divergence(data, datapred)
        eq_(expected, actual, "relative entropy values differ")

        data = {"heads": 0.5, "tails": 0.5}
        datapred = {"heads": 0.25, "tails": 0.75}
        expected = 0.20751874963942185
        actual = b.kullback_leibler_divergence(data, datapred)
        eq_(expected, actual, "relative entropy values differ")

    def test_sensitivity(self):
        pass

    def test_positive_predictive_value(self):
        pass

    def test_f_score(self):
        pass
