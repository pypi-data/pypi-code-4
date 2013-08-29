#! python
# -*- coding: utf-8 -*-

import subprocess
import shutil

build_folder = os.path.join(os.environ['TEMP'],
            'pip_build_' + os.environ['USERNAME'] + '_pyinstruments')
if os.path.exists(build_folder):
    shutil.rmtree(build_folder)
subprocess.call(['pip', 
                 'install',
                 'pyivi', 
                 '-I', 
                 '-U', 
                 '-b', 
                 build_folder])

