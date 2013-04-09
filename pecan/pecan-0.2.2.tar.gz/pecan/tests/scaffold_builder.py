import os
import sys
import subprocess
import urllib2
import time


if sys.version_info < (2, 7):
    import unittest2 as unittest
else:
    import unittest  # noqa

from pecan.tests import PecanTestCase


if __name__ == '__main__':

    class TestTemplateBuilds(PecanTestCase):
        """
        Used to test the templated quickstart project(s).
        """

        @property
        def bin(self):
            return os.path.dirname(sys.executable)

        def poll(self, proc):
            limit = 30
            for i in range(limit):
                proc.poll()

                # Make sure it's running
                if proc.returncode is None:
                    break
                elif i == limit:  # pragma: no cover
                    raise RuntimeError("Server process didn't start.")
                time.sleep(.1)

        def test_project_pecan_serve_command(self):
            # Start the server
            proc = subprocess.Popen([
                os.path.join(self.bin, 'pecan'),
                'serve',
                'testing123/config.py'
            ])

            try:
                self.poll(proc)
                retries = 30
                while True:
                    retries -= 1
                    if retries < 0:  # pragma: nocover
                        raise RuntimeError(
                            "The HTTP server has not replied within 3 seconds."
                        )
                    try:
                        # ...and that it's serving (valid) content...
                        resp = urllib2.urlopen('http://localhost:8080/')
                        assert resp.getcode() == 200
                        assert 'This is a sample Pecan project.' in resp.read()
                    except urllib2.URLError:
                        pass
                    else:
                        break
                    time.sleep(.1)
            finally:
                proc.terminate()

        def test_project_pecan_shell_command(self):
            # Start the server
            proc = subprocess.Popen([
                os.path.join(self.bin, 'pecan'),
                'shell',
                'testing123/config.py'
            ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                stdin=subprocess.PIPE
            )

            self.poll(proc)

            out, _ = proc.communicate(
                '{"model" : model, "conf" : conf, "app" : app}'
            )
            assert 'testing123.model' in out, out
            assert 'Config(' in out, out
            assert 'webtest.app.TestApp' in out, out

            try:
                # just in case stdin doesn't close
                proc.terminate()
            except:
                pass

    class TestGunicornServeCommand(TestTemplateBuilds):

        def poll_gunicorn(self, proc, port):
            try:
                self.poll(proc)
                retries = 30
                while True:
                    retries -= 1
                    if retries < 0:  # pragma: nocover
                        raise RuntimeError(
                            "The gunicorn server has not replied within"
                            " 3 seconds."
                        )
                    try:
                        # ...and that it's serving (valid) content...
                        resp = urllib2.urlopen('http://localhost:%d/' % port)
                        assert resp.getcode() == 200
                        assert 'This is a sample Pecan project.' in resp.read()
                    except urllib2.URLError:
                        pass
                    else:
                        break
                    time.sleep(.1)
            finally:
                proc.terminate()

        def test_serve_from_config(self):
            # Start the server
            proc = subprocess.Popen([
                os.path.join(self.bin, 'gunicorn_pecan'),
                'testing123/config.py'
            ])

            self.poll_gunicorn(proc, 8080)

        def test_serve_with_custom_bind(self):
            # Start the server
            proc = subprocess.Popen([
                os.path.join(self.bin, 'gunicorn_pecan'),
                '--bind=0.0.0.0:9191',
                'testing123/config.py'
            ])

            self.poll_gunicorn(proc, 9191)

    # First, ensure that the `testing123` package has been installed
    args = [
        os.path.join(os.path.dirname(sys.executable), 'pip'),
        'install',
        '-U',
        '-e',
        './testing123'
    ]
    process = subprocess.Popen(args)
    _, unused_err = process.communicate()
    assert not process.poll()

    unittest.main()
