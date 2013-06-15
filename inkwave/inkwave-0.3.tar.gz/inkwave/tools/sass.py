import os
from subprocess import Popen, PIPE
from inkwave.core import env


def sass(content, scss=False, style='compact', load_path=[]):
    cmd = ['sass', '-s']
    cmd += ['-t', style]
    cmd += ['--cache-location', os.path.join(env.cache_path, 'sass')]
    for p in load_path:
        cmd += ['-I', os.path.join(env.root, p)]
    if scss:
        cmd.append('--scss')

    with Popen(cmd, bufsize=-1,
               stdin=PIPE, stdout=PIPE) as proc:
        out, errs = proc.communicate(content)
        if errs:
            raise RuntimeError(errs)
        return out
