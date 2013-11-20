"""
Contains build utilities for concatenating files
"""
import logging
import os

from fabric.api import env

from util import get_files


logger = logging.getLogger(__name__)


def concat(files=None, output=None, banner=None, line_sep=None, clean=True):
    """
    Concatenates together files and writes them to output

    :param files: List of files or dict to pass to get_files for all files to run against
    :param output: the location to output the resulting file
    :param banner: A top banner string to add to the file
    :param line_sep: The character with which the files will be concatenated
    :param clean: If True, removes the output file before running concat.
    """

    logger.debug("Running concat function. Files: " + str(files))

    if files is None or output is None:
        raise Exception("Must run concat with files and output location")

    if clean and os.path.exists(output):
        os.remove(output)

    line_sep = line_sep or "\n"

    files = get_files(files)

    if not getattr(env, 'dry_run', False):
        out_data = banner or ""
        for path in files:
            if not os.path.exists(path) or not os.path.isfile(path):
                continue

            with open(path, 'r') as f:
                out_data = line_sep.join([out_data, f.read()])

        with open(output, 'w') as f:
            f.write(out_data)

    logger.info("Successfully concatenated {} files/folders to {}".format(len(files), output))
    logger.debug("Files/Folders concatenated: \n" + "\n".join(files))


