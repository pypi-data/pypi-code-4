import logging,logging.handlers
import traceback,imp,sys
if sys.version_info[0]==2:
	from StringIO import StringIO
elif sys.version_info[0]>=3:
	from io import StringIO
from os.path import join


def get_traceback():
	strio = StringIO()
	traceback.print_exc(file=strio)
	return strio.getvalue()

pysite_logger = None

def logger(conf):
	global pysite_logger
	if not pysite_logger:
		log_filename = conf.logfile
		pysite_logger = logging.getLogger(conf.sitename)
		pysite_logger.setLevel(logging.DEBUG)

		# Add the log message handler to the logger
		if len(pysite_logger.handlers)==0:
			handler = logging.handlers.RotatingFileHandler(log_filename, maxBytes=4000000, backupCount=5)
			formatter = logging.Formatter("%(asctime)s - %(message)s")
			handler.setFormatter(formatter)
			pysite_logger.addHandler(handler)
	return pysite_logger