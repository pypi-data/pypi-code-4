import unittest


def suite():
    return unittest.TestLoader().discover("cron_monitor.tests",
                                          pattern="test*.py")
