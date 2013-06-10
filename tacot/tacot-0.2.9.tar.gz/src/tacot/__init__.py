# -*- coding: utf-8 -*-
import os
import shutil
import time
import fnmatch
import codecs
import argparse
from StringIO import StringIO

from mako.template import Template
from mako.lookup import TemplateLookup

from tacot.manifest import Manifest, findall


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
        result = "global-include *\nprune _build/\nprune includes/\nexclude .manifest"

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


def process(root_path, build_path, manifest_content, verbose):
    template_lookup = TemplateLookup(
        directories=[root_path],
        output_encoding='utf-8',
        encoding_errors='replace'
    )

    if verbose:
        print("Please wait, tacot process files :\n")

    for source_filepath in file_to_process_iter(root_path, manifest_content):
        dest_filepath = os.path.join(build_path, source_filepath)
        if verbose:
            print(source_filepath)

        if not os.path.exists(os.path.dirname(dest_filepath)):
            os.makedirs(os.path.dirname(dest_filepath))

        if fnmatch.fnmatch(source_filepath, "*.html"):
            render_and_copy(
                source_filepath, dest_filepath, template_lookup, root_path
            )
        elif fnmatch.fnmatch(source_filepath, "*.mako"):
            render_and_copy(source_filepath, dest_filepath[:-len('.mako')],
                            template_lookup, root_path)
        else:
            shutil.copy(source_filepath, dest_filepath)


def render_and_copy(source, dest, lookup, root_path):
    f = codecs.open(source, "r", "utf8")
    data = f.read()
    f.close()
    t = Template(data, lookup=lookup, uri=source)
    f = codecs.open(dest, "w", "utf8")
    f.write(t.render_unicode(
        root_path=RootPath(os.path.relpath(root_path, os.path.dirname(source))),
        current_page=source,
        g=type("Global", (object,), {})
    ))
    f.close()


def main():
    parser = argparse.ArgumentParser(
        description="""A tool to generate a static web site, with Mako templates."""
    )
    parser.add_argument(
        dest="path", nargs="?", default=os.getcwd(),
        help="""Path where to find the content files"""
    )
    parser.add_argument(
        "-o", "--output",
        dest="output", default=os.path.join(os.getcwd(), "_build"),
        help="""Where to output the generated files. If not specified, a directory """
             """will be created, named "_build" in the current path (_build by default)."""
    )
    parser.add_argument(
        "-m", "--manifest",
        dest="manifest", default=None,
        help="""Manifest config file (.manifest by default in root content files folder)"""
    )
    parser.add_argument(
        "-r", "--autoreload",
        dest="autoreload", action="store_true",
        help="Relaunch tacot each time a modification occurs on the content files"
    )
    parser.add_argument(
        "-v", "--verbose",
        dest="verbose", action="store_true",
        help="Enable verbose mode"
    )

    options = parser.parse_args()

    root_path = os.path.join(
        os.getcwd(),
        options.path
    )
    build_path = os.path.join(
        os.getcwd(),
        options.output
    )
    if options.manifest:
        manifest_file_path = os.path.join(
            os.getcwd(),
            options.manifest
        )
    else:
        manifest_file_path = os.path.join(root_path, '.manifest')

    os.chdir(root_path)
    manifest_content = get_manifest_content(manifest_file_path)

    if options.verbose:
        print('Path source : %s' % root_path)
        print('Build target : %s' % build_path)
        print('Manifest file : %s' % manifest_file_path)
        print('=== Manifest file content ===')
        print(manifest_content)
        print('=============================')

    if options.autoreload:
        while True:
            try:
                if files_changed(root_path, build_path):
                    process(
                        root_path,
                        build_path,
                        manifest_content,
                        options.verbose
                    )

                time.sleep(.5)  # sleep to avoid cpu load
            except KeyboardInterrupt:
                break

    else:
        process(
            root_path,
            build_path,
            manifest_content,
            options.verbose
        )
