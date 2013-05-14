import sys
import os
import time
import signal
import logging
import tempfile

from unittest import TestCase

from abl.util import Popen, ProcessTimoutError

logger = logging.getLogger(__name__)

class TestProcesses(TestCase):

    def setUp(self):
        logging.basicConfig(
            stream=sys.stderr,
            level=logging.DEBUG,
            )


    def sigterm_ignorer(self):
        tf = tempfile.mktemp()
        cmd = [sys.executable, os.path.join(os.path.dirname(__file__), "sigterm_ignorer.py"), tf]
        p = Popen(cmd)
        while not os.path.exists(tf):
            pass
        os.remove(tf)
        return p



    def test_timeout(self):
        calls = [name for name in dir(Popen) if hasattr(getattr(Popen, name), "_timeoutcall")]
        assert calls
        for timeoutcall in calls:
            p = Popen(["sleep", "5"], timeout=.5)
            self.assertRaises(
                ProcessTimoutError,
                getattr(p, timeoutcall),
                )


    def test_timeout_passes(self):
        calls = [name for name in dir(Popen) if hasattr(getattr(Popen, name), "_timeoutcall")]
        assert calls
        for timeoutcall in calls:
            p = Popen(["sleep", "1"], timeout=2.0)
            getattr(p, timeoutcall)()



    def test_kill_after_process_is_terminated(self):
        p = Popen(["sleep", "0"])
        p.wait()
        p.kill()


    def test_sigkill(self):
        p = self.sigterm_ignorer()
        time.sleep(.2)
        p.kill()

        for _ in xrange(10):
            rc = p.poll()
            if rc is not None:
                break
            time.sleep(.1)

        assert rc is None

        assert p.kill(signal.SIGKILL)
        for _ in xrange(10):
            rc = p.poll()
            if rc is not None:
                break
            time.sleep(.1)

        self.assertEqual(rc, -signal.SIGKILL)


    def test_annihilate_with_sigkill(self):
        logger.debug("test_annihilate_with_sigkill")
        p = self.sigterm_ignorer()
        rc = p.annihilate(tries=2, pause=.1)
        self.assertEqual(
            rc,
            -signal.SIGKILL,
            )


    def test_annihilate_with_sigterm(self):
        p = Popen(["sleep", "20"])

        self.assertEqual(
            p.annihilate(pause=.1),
            -signal.SIGTERM,
            )
