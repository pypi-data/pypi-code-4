"""
build utilities for Jade templates
"""
import logging

from fabric.api import env

from util import get_files, build_run

logger = logging.getLogger(__name__)


def jade(files=None, obj=None, out=None, path=None, pretty=False, client=False, no_debug=False, watch=False):
    """

    Compiles jade templates

    :param files: List of files or dict to pass to get_files for all files to run against
    :param obj: javascript options object
    :param out: output the compiled html to <dir>
    :param path: filename used to resolve includes
    :param pretty: compile pretty html output
    :param client: compile function for client-side runtime.js
    :param no_debug: compile without debugging (smaller functions)
    :param watch: watch files for changes and automatically re-render
    """

    logger.debug("Running jade function. Files: " + str(files))

    if files is None:
        raise Exception("Must run jade with files")

    if isinstance(files, dict):
        # Some sane defaults for jade if not specified
        files['only_files'] = True
        if 'recursive' not in files:
            files['recursive'] = True
        if 'match' not in files:
            files['match'] = ['*jade', ]

    files = get_files(files)

    compile_paths = ' '.join(['"{}"'.format(f) for f in files])

    if not getattr(env, 'dry_run', False):
        opts = []
        if obj:
            opts.append('-O "{}"'.format(obj))
        if out:
            opts.append('-o "{}"'.format(out))
        if path:
            opts.append('-p "{}"'.format(path))
        if pretty:
            opts.append('-P')
        if client:
            opts.append('-c')
        if no_debug:
            opts.append('-D')
        if watch:
            opts.append('-w')

        build_run("jade {} {}".format(' '.join(opts), compile_paths),
                  async=watch, keep_alive=1 if watch else 0)

    logger.info("Successfully compiled {} jade files".format(len(files)))
    logger.debug("Files compiled: \n" + "\n".join(files))

