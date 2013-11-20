"""
Build utilities for Coffeescript
"""
import logging

from fabric.api import env

from util import get_files, build_run

logger = logging.getLogger(__name__)


def coffee(files=None, bare=False, lint=False, map=False, join=None, output=None, watch=False):
    """
    Compiles coffeescript files

    :param files: List of files or dict to pass to get_files for all files to run against
    :param bare: output bare coffeescript
    :param lint: run through jslint
    :param map: generate source maps
    :param join: join together files to this output location (string path)
    :param output: directory to output files
    :param watch: True to watch the output and recompile on changes
    """

    logger.debug("Running coffee function. Files: " + str(files))

    if files is None:
        raise Exception("Must run coffee with files")

    if isinstance(files, dict):
        # Some sane defaults for coffeescript if not specified
        files['only_files'] = True
        if 'recursive' not in files:
            files['recursive'] = True
        if 'match' not in files:
            files['match'] = ['*coffee', ]

    files = get_files(files)

    compile_paths = ' '.join(['"{}"'.format(f) for f in files])

    if not getattr(env, 'dry_run', False):
        opts = []
        if bare:
            opts.append('-b')
        if join:
            opts.append('-j "{}"'.format(join))
        if lint:
            opts.append('-l')
        if map:
            opts.append('-m')
        if watch:
            opts.append('-w')
        if output:
            opts.append('-o "{}"'.format(output))

        build_run("coffee {} -c {}".format(' '.join(opts), compile_paths),
                  async=watch, keep_alive=1 if watch else 0)

    logger.info("Successfully compiled {} coffeescript files".format(len(files)))
    logger.debug("Files compiled: \n" + "\n".join(files))

