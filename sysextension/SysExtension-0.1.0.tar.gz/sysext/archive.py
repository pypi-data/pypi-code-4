# coding: utf-8

import subprocess as sp

# TODO Add function to generically decompress any file, intuitively picking
#        the correct decompressor
# TODO Add target_dir='.' argument to all of these, raise if target_dir already
#        exists
# TODO It would be slightly better to use the built-in libraries: tar, bz2,
#        gzip, and zipfile


def untar(tarball):
    args = 'xf'
    if tarball.endswith('.bz2'):
        args += 'j'

    command_line = ['tar', args, tarball]

    return sp.check_call(command_line)


def unzip(zipfile, stdout=None):
    args = ['unzip']

    if not stdout:
        args.append('-qq')

    args.append(zipfile)

    return sp.check_call(args, stdout=stdout)


def bunzip2(bzipfile):
    args = ['bunzip2', '-f']
    args.append(bzipfile)

    return sp.check_call(args)
