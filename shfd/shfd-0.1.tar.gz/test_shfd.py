# -*- coding: utf-8 -*-

from __future__ import print_function, unicode_literals

import sys
import unittest
import shfd
import logging


# logging output
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter('%(levelname)s - %(name)s - %(message)s'))
logging.root.addHandler(handler)
logging.root.setLevel(logging.INFO)


class TestShfd(unittest.TestCase):

    def test_run(self):
        ret = shfd.run('echo "hello world"')
        self.assertEqual(ret.out, 'hello world\n')
        self.assertEqual(ret.err, '')

    def test_unicode_api(self):
        cmds = [
            shfd.run('echo "hello world"'),
            shfd.run('echo "hello world"'.encode()),
        ]

        for ret in cmds:
            self.assertTrue(isinstance(ret.out, shfd.unicode))
            self.assertTrue(isinstance(ret.err, shfd.unicode))

    def test_eq(self):
        c = shfd.cmd('echo "hello world"')
        # cmd == cmd
        self.assertEqual(c, c)
        # cmd == str
        self.assertEqual(c, 'echo "hello world"')

    def test_pipe(self):
        cmds = [
            shfd.cmd('echo "hello world"') | shfd.cmd('head') | shfd.cmd('tail'),
            shfd.cmd('echo "hello world"') | 'head' | shfd.cmd('tail'),
        ]

        for i, cmd in enumerate(cmds):
            self.assertTrue(isinstance(cmd, shfd.cmd))
            # multi call support
            for j in range(2):
                ret = cmd.run()
                self.assertEqual(ret.out, 'hello world\n')
                self.assertEqual(ret.err, '')
                self.assertEqual(ret.command, 'echo "hello world" | head | tail')
                self.assertEqual(ret.history, ['echo "hello world"', 'head'])
                for history_cmd in ret.history:
                    self.assertEqual(history_cmd.out, 'hello world\n')
                    self.assertEqual(history_cmd.err, '')

# python 2.6 not support unittest.skip
'''
    @unittest.skip("useless feature")
    def test_required_success_pire(self):
        cmd = ((shfd.cmd('echo') & 'head') & 'tail') | 'tail'
        cmd.run()
        self.assertListEqual([i.command for i in cmd.history], [
            'echo',
            'echo & head',
            'echo & head & tail',
        ])
        self.assertEqual(cmd.command, 'echo & head & tail | tail')
        self.assertListEqual(
            [c.retcode for c in cmd.history] + [cmd.retcode],
            [0, 0, 0, 0]
        )

        cmd = ((shfd.cmd('head -w') & 'head') | 'tail') & 'tail'
        self.assertListEqual([i.command for i in cmd.history], [
            'head -w',
            'head -w & head',
            'head -w & head | tail',
        ])
        #cmd = shfd.cmd('head -w')
        #cmd &= 'head'
        #cmd |= 'tail'
        #cmd &= 'tail'
        self.assertEqual(cmd.command, 'head -w & head | tail & tail')
        cmd.run()
        self.assertListEqual(
            [c.retcode for c in cmd.history] + [cmd.retcode],
            [1, None, 0, 0]
        )
'''

if __name__ == '__main__':
    unittest.main()
