"""
Contains methods for cleaning output
"""
import logging
import os
import shutil

from fabric.api import env

from util import get_files


logger = logging.getLogger(__name__)


def clean(files=None):
    """

    Cleans the given files

    :param files: List of files or dict to pass to get_files for all files to run against.

    """

    logger.debug("Running clean function. Files: " + str(files))

    if files is None:
        raise Exception("Must run clean with files")

    if isinstance(files, dict):
        if not os.path.exists(files['path']):
            logger.debug("Clean path does not exist. Clean considered successful.")
            return

    files = get_files(files)

    if not getattr(env, 'dry_run', False):
        for path in files:
            if not os.path.exists(path):
                continue

            if os.path.isfile(path):
                os.remove(path)
            else:
                shutil.rmtree(path)

    logger.info("Successfully cleaned {} files/folders".format(len(files)))
    logger.debug("Files/Folders removed: \n" + "\n".join(files))


