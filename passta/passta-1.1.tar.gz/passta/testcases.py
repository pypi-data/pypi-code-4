import os
import shutil
from tempfile import mkdtemp


class PopenTestcase:
    def setup(self):
        self.tmp_dir = mkdtemp()
        self.old_path = os.environ['PATH']
        os.environ['PATH'] = self.tmp_dir

    def teardown(self):
        shutil.rmtree(self.tmp_dir)
        os.environ['PATH'] = self.old_path

    def create_sh(self, name, content='', mode=0o755):
        bin_path = os.path.join(self.tmp_dir, name)
        try:
            os.makedirs(os.path.dirname(bin_path))
        except OSError:
            pass
        with open(bin_path, 'w') as f:
            f.write('#!/bin/sh\n')
            f.write(content)
        os.chmod(bin_path, mode)
        return bin_path

    def path_append(self, dir_):
        os.environ['PATH'] += '{}{}'.format(
            os.pathsep, os.path.join(self.tmp_dir, dir_))
