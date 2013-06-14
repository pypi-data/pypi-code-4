# -*- coding: utf-8 -*-
"""tacot - a tool to generate a static web site, with Mako templates.

Usage:
    tacot [<path> --output=<output> -v -m=<manifest> --autoreload --assets=<assets> --force]
    tacot --version


Options:
    <path>              Path where to find the content files. By default
                        it is the current folder.
    -h, --help          Show this screen.
    --version
    -o=<output>, --output=<output>
                        Where to output the generated files. If not specified,
                        a directory will be created, named "_build" in the
                        current path (default: _build).
    -m=<manifest>, --manifest=<manifest>
                        Manifest config file (default: <path>/.manifest).
    -r, --autoreload    Relaunch tacot each time a modification occurs on the
                        content files
    --assets=<assets>   Assets config file (default: <path>/.assets.yaml).
    -f, --force         If force isn't used, tacot parse or copy only source
                        file newer that the same file in output folder.
    -v, --verbose       Enable verbose mode


Documentation : http://pythonhosted.org/tacot/

Example:

    $ tacot src -o _build -v

"""
__version__ = '0.3.2'

import os
import sys
import shutil
import time
import fnmatch
import codecs
import logging
from StringIO import StringIO

from mako.template import Template
from mako.lookup import TemplateLookup
from webassets.loaders import YAMLLoader
from webassets.script import CommandLineEnvironment

from tacot.manifest import Manifest, findall
from tacot.docopt import docopt


class RootPath(object):
    def __init__(self, root_path):
        self.root_path = [root_path.strip("/")]
        if self.root_path[0] == '.':
            self.root_path = []

    def __call__(self, path):
        return "/".join(self.root_path + [path.lstrip("/")])


def get_manifest_content(manifest_file_path):
    if os.path.exists(manifest_file_path):
        f = open(manifest_file_path)
        result = f.read()
        f.close()
    else:
        result = "global-include *\nprune _build/\nprune includes/\nexclude .manifest .assets.yaml .bowerrc bower.json"

    return result


def file_to_process_iter(root_path, manifest_content):
    manifest = Manifest()
    manifest.findall(root_path.rstrip('/') + '/')

    manifest.read_template(
        StringIO(manifest_content)
    )

    return manifest.files

LAST_MTIME = 0


def files_changed(root_path, build_path):
    """Return True if the files have changed since the last check"""

    def file_times():
        """Return the last time files have been modified"""
        current_folder = None
        for file in findall(root_path):
            p = os.path.join(root_path, file.lstrip("/"))
            if p.startswith(build_path):
                continue

            if os.path.dirname(p) != current_folder:
                current_folder = p
                yield os.stat(os.path.dirname(p)).st_mtime

            yield os.stat(p).st_mtime

    global LAST_MTIME
    mtime = max(file_times())
    if mtime > LAST_MTIME:
        LAST_MTIME = mtime
        return True
    return False


def process(root_path, build_path, manifest_content, verbose, assets_file_path=None, force=False):
    if assets_file_path and os.path.exists(assets_file_path):
        log = logging.getLogger('assets')
        log.addHandler(logging.StreamHandler())
        log.setLevel(logging.WARN)

        loader = YAMLLoader(assets_file_path)
        assets_env = loader.load_environment()
        cmdenv = CommandLineEnvironment(assets_env, log)
        cmdenv.invoke('build', {})
    else:
        assets_env = None

    template_lookup = TemplateLookup(
        directories=[root_path],
        output_encoding='utf-8',
        encoding_errors='replace'
    )

    if verbose:
        print("Please wait, tacot process files :\n")

    for source_filepath in file_to_process_iter(root_path, manifest_content):
        dest_filepath = os.path.join(build_path, source_filepath)

        if not os.path.exists(os.path.dirname(dest_filepath)):
            os.makedirs(os.path.dirname(dest_filepath))

        if (
            force or
            (not os.path.exists(dest_filepath)) or
            (os.path.getmtime(source_filepath) > os.path.getmtime(dest_filepath))
        ):
            if fnmatch.fnmatch(source_filepath, "*.html"):
                render_and_copy(
                    source_filepath,
                    dest_filepath,
                    template_lookup,
                    root_path,
                    assets_env
                )
                if verbose:
                    print("%s parsed to %s" % (source_filepath, dest_filepath))
            elif fnmatch.fnmatch(source_filepath, "*.mako"):
                render_and_copy(
                    source_filepath,
                    dest_filepath[:-len('.mako')],
                    template_lookup,
                    root_path,
                    assets_env
                )
                if verbose:
                    print("%s parsed to %s" % (source_filepath, dest_filepath[:-len('.mako')]))
            else:
                shutil.copy(source_filepath, dest_filepath)
                if verbose:
                    print("%s copied to %s" % (source_filepath, dest_filepath))
        else:
            if verbose:
                print("%s ignored" % source_filepath)


def render_and_copy(source, dest, lookup, root_path, assets_env=None):
    f = codecs.open(source, "r", "utf8")
    data = f.read()
    f.close()
    t = Template(data, lookup=lookup, uri=source)
    f = codecs.open(dest, "w", "utf8")
    f.write(t.render_unicode(
        root_path=RootPath(os.path.relpath(root_path, os.path.dirname(source))),
        current_page=source,
        g=type("Global", (object,), {}),
        assets=assets_env
    ))
    f.close()


def main():
    arguments = docopt(__doc__)

    if arguments['--version']:
        print(__version__)
        sys.exit()

    if arguments['<path>'] is None:
        root_path = os.getcwd()
    else:
        root_path = os.path.join(
            os.getcwd(),
            arguments['<path>']
        )

    if arguments['--output'] is None:
        arguments['--output'] = '_build'

    build_path = os.path.join(
        os.getcwd(),
        arguments['--output']
    )
    if arguments['--manifest'] is None:
        manifest_file_path = os.path.join(root_path, '.manifest')
    else:
        manifest_file_path = os.path.join(
            os.getcwd(),
            arguments['--manifest']
        )

    if arguments['--assets'] is None:
        assets_file_path = os.path.join(root_path, '.assets.yaml')
    else:
        assets_file_path = os.path.join(
            os.getcmd(),
            arguments['--assets']
        )

    os.chdir(root_path)
    manifest_content = get_manifest_content(manifest_file_path)

    if arguments['--verbose']:
        print('Path source : %s' % root_path)
        print('Build target : %s' % build_path)
        print('Manifest file : %s' % manifest_file_path)
        print('Assets file : %s' % assets_file_path)
        print('=== Manifest file content ===')
        print(manifest_content)
        print('=============================')

    if arguments['--autoreload']:
        while True:
            try:
                if files_changed(root_path, build_path):
                    process(
                        root_path,
                        build_path,
                        manifest_content,
                        arguments['--verbose'],
                        assets_file_path=assets_file_path,
                        force=arguments['--force']
                    )

                time.sleep(.5)  # sleep to avoid cpu load
            except KeyboardInterrupt:
                break

    else:
        process(
            root_path,
            build_path,
            manifest_content,
            arguments['--verbose'],
            assets_file_path=assets_file_path,
            force=arguments['--force']
        )
