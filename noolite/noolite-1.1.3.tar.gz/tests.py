import unittest

import noolite

init_cmd = [0x30, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]


class Tests(unittest.TestCase):
    def test_init_ch_type(self):
        with self.assertRaises(ValueError):
            switcher = noolite.NooLite(channals="bla", tests=True)
            switcher = noolite.NooLite(idVendor="bla", tests=True)

    def test_init_idVendor_type(self):
        with self.assertRaises(ValueError):
            switcher = noolite.NooLite(idVendor="bla", tests=True)

    def test_init_idProduct_type(self):
        with self.assertRaises(ValueError):
            switcher = noolite.NooLite(idProduct="bla", tests=True)

    def test_ch_str(self):
        switcher = noolite.NooLite(tests=True)
        cmd = init_cmd
        cmd[4] = 7
        cmd[1] = 0x02
        self.assertEqual(switcher.on("7"), cmd)

    def test_ch_int(self):
        switcher = noolite.NooLite(tests=True)
        cmd = init_cmd
        cmd[4] = 7
        cmd[1] = 0x00
        self.assertEqual(switcher.off(7), cmd)

    def test_ch_negative(self):
        switcher = noolite.NooLite(tests=True)
        self.assertRaises(noolite.NooLiteErr, switcher.on, -1)

    def test_ch_too_big(self):
        switcher = noolite.NooLite(tests=True)
        self.assertRaises(noolite.NooLiteErr, switcher.on, 42)

    def test_set(self):
        switcher = noolite.NooLite(tests=True)
        value = 50
        cmd = init_cmd
        cmd[4] = 7
        cmd[2] = 0x01
        cmd[1] = 0x06
        cmd[5] = 35 + value
        self.assertEqual(switcher.set(7, value), cmd)

    def test_set_str(self):
        switcher = noolite.NooLite(tests=True)
        value = "70"
        cmd = init_cmd
        cmd[4] = 7
        cmd[2] = 0x01
        cmd[1] = 0x06
        cmd[5] = 35 + int(value)
        self.assertEqual(switcher.set(7, value), cmd)

    def test_set_zero(self):
        switcher = noolite.NooLite(tests=True)
        value = 0
        cmd = init_cmd
        cmd[4] = 7
        cmd[2] = 0x01
        cmd[1] = 0x06
        cmd[5] = 0
        self.assertEqual(switcher.set(7, value), cmd)
