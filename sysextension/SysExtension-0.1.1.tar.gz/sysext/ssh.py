# coding: utf-8

import subprocess as sp


def append_contents(host, remote_path, local_file):
    # This is used instead of check_output to be compatible with Python 2.6
    output = sp.Popen(['ssh', '-o', 'StrictHostKeyChecking=no', host, 'cat %s' % (remote_path)], stdout=sp.PIPE).communicate()[0]

    if not output:
        raise Exception('No contents were received')

    with open(local_file, 'ab') as f:
        f.write(output)


def copy(remote_file_path, local_file, stdout=None):
    args = ['scp', '-o', 'StrictHostKeyChecking=no']

    if not stdout:
        args.append('-q')

    args.extend([remote_file_path, local_file])

    sp.check_call(args, stdout=stdout)
