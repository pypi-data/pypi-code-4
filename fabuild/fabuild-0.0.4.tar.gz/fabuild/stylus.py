"""
build utilities for Stylus templates
"""
import logging

from fabric.api import env

from util import get_files, build_run

logger = logging.getLogger(__name__)


def stylus(files=None, use=None, inline=False, out=None,
           include=False, compress=False, firebug=False,
           import_styl=None, include_css=False, resolve_url=False, watch=False):
    """
    Compiles stylus templates

    :param files: List of files or dict to pass to get_files for all files to run against
    :param use: Utilize the Stylus plugin at <path>
    :param inline: Utilize image inlining via data URI support
    :param out: output the compiled css to <dir>
    :param include: Add <path> to lookup paths
    :param compress: compress css output
    :param firebug: Emits debug infos in the generated CSS that can be used by the FireStylus Firebug plugin
    :param import_styl: Import stylus <file>
    :param include_css: Include regular CSS on @import
    :param resolve_url: Resolve relative urls inside imports
    :param watch: watch files for changes and automatically re-render
    """

    logger.debug("Running stylus function. Files: " + str(files))

    if files is None:
        raise Exception("Must run stylus with files")

    if isinstance(files, dict):
        # Some sane defaults for stylus if not specified
        files['only_files'] = True
        if 'recursive' not in files:
            files['recursive'] = True
        if 'match' not in files:
            files['match'] = ['*styl', ]

    files = get_files(files)

    compile_paths = ' '.join(['"{}"'.format(f) for f in files])

    if not getattr(env, 'dry_run', False):
        opts = []
        if use:
            opts.append('-u "{}"'.format(use))
        if inline:
            opts.append('-U')
        if watch:
            opts.append('-w')
        if out:
            opts.append('-o "{}"'.format(out))
        if include:
            opts.append('-I "{}"'.format(include))
        if compress:
            opts.append('-c')
        if firebug:
            opts.append('-f')
        if resolve_url:
            opts.append('-r')
        if include_css:
            opts.append('--include-css')
        if import_styl:
            opts.append('--import "{}"'.format(import_styl))

        build_run("stylus {} {}".format(' '.join(opts), compile_paths),
                  async=watch, keep_alive=1 if watch else 0)

    logger.info("Successfully compiled {} stylus files".format(len(files)))
    logger.debug("Files compiled: \n" + "\n".join(files))
