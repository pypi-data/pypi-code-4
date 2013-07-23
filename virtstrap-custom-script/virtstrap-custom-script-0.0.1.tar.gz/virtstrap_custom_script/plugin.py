from __future__ import with_statement
import os
from virtstrap import hooks
from virtstrap.log import logger
from virtstrap.utils import call_subprocess, in_directory


#FIXME need to add this as a virtstrap util
def which(program):
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None


@hooks.create('install', ['after'])
def install_script_packages(event, options, project=None, **kwargs):
    # ensure we're in the project's root directory
    with in_directory(project.path()):
        install_script = project.path('./scripts/install.sh')
        if not os.path.exists(install_script):
            return

        # Installs the bundle requirements and the bins for each
        # requirement in the project's bin path
        call_subprocess(['bash', install_script, project.env_path()])


@hooks.create('environment', ['after'])
def add_npm_bin_path(event, options, project=None, **kwargs):
    with in_directory(project.path()):
        env_script = project.path('./scripts/env.sh')
        if not os.path.exists(env_script):
            return

        env_file_path = options.env_file
        env_file = open(env_file_path, 'a')
        env_file.write('\n# EXTEND ENV WITH CUSTOM SCRIPT\n')
        env_file.write('. %s' % env_script)
        env_file.close()
