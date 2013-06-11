import unittest
from mock import patch
from ..platform import get_platform
from ..platform import OSX
from ..platform import LINUX


class TestPlatform(unittest.TestCase):

    def test_get_platform_osx(self):
        with patch('nosealert.platform.sys') as sys:
            sys.platform = 'darwin'
            self.assertEqual(get_platform(), OSX)

    def test_get_platform_linux(self):
        with patch('nosealert.platform.sys') as sys:
            sys.platform = 'linux2'
            self.assertEqual(get_platform(), LINUX)

            sys.platform = 'Linux2'
            self.assertEqual(get_platform(), LINUX)

            sys.platform = 'Arch-Linux-Foo-Bar'
            self.assertEqual(get_platform(), LINUX)

    def test_get_platform_raises_runtime_error(self):
        with patch('nosealert.platform.sys') as sys:
            sys.platform = 'win32'
            self.assertRaises(RuntimeError, get_platform)

