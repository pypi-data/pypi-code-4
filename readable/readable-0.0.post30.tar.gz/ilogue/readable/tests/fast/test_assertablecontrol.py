#!/usr/bin/python
# -*- coding: utf-8 -*-
#   Copyright 2010 Jasper van den Bosch <jasper@ilogue.com>

import unittest
from mock import Mock
from webtest import Submit
from ilogue.readable import assertionMethod


class AssertableControlTestCase(unittest.TestCase):
    pass
#    def test_whichIsDisabled_asserts_that_the_last_matched_control_is_disabled(self):
#        from ilogue.readable.AssertableControl import AssertableControl
#        disabledSubmit = self.
#        enabledSubmit = 
#        (assertionMethod(disabledSubmit.whichIsDisabled)
#            .doesNotFail())
#        (assertionMethod(enabledSubmit.whichIsDisabled)
#            .fails())


if __name__ == '__main__':
    unittest.main()
