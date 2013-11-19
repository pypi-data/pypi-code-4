__author__ = 'alexey.grachev'
import zipfile
import logging
import os
import sys
import fnmatch

def unpack(issue, arguments):
    try:
        logging.info("------------------------------Unpacking")
        issue.setStatus("Unpacking")
        arcDest = os.path.join(arguments.outputDir, issue.dest())

        zfile = zipfile.ZipFile(issue.archive())
        for name in zfile.namelist():
            if any(fnmatch.fnmatch(name, filter) for filter in arguments.logFilesFilter):
                logging.info('Unpacking {0}'.format(name))
                zfile.extract(name, arcDest)
                issue.setUnpacked(arcDest)
            else:
                logging.debug('Skipping {0}'.format(name))


        issue.setStatus("Unpacked")
    except Exception as e:
        logging.error(str(e))
        logging.debug('Traceback', exc_info=sys.exc_info())
        raise Exception('Failed to unpack archive')

