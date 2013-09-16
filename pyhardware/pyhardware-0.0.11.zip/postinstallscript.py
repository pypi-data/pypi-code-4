#! python
# -*- coding: utf-8 -*-

import os
import subprocess
import shutil

build_folder = os.path.join(os.environ['TEMP'], 
                            'pip_build_' + os.environ['USERNAME'],
                            'pyivi')
if os.path.exists(build_folder):
    shutil.rmtree(build_folder)
if subprocess.call(['pip', 
                 'install',
                 'pyivi', 
                 '-I', 
                 '-U']):
    raise RuntimeError('problem installing pyivi')

