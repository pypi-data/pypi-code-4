import unittest


class StartupTests(unittest.TestCase):
    def test_basic_import(self):
        from docker_startup import (Startup, DjangoStartup, PHPStartup,
                                    JavaStartup)
