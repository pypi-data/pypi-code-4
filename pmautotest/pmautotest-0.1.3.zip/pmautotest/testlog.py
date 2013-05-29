import logging
import os

def logged_class(cls):
	cur_path = os.path.abspath('.') + "\\log"
	if os.path.isdir(cur_path):
		pass
	else:
		os.mkdir(cur_path)
	filename = cur_path + "\\%s.log"%cls.__name__
	cls.log = logging.getLogger('{0}'.format(cls.__name__))
	cls.log.setLevel(logging.DEBUG)
	handler = logging.FileHandler(filename,mode='w') 
	handler.setLevel(logging.NOTSET)
	formatter = logging.Formatter('%(name)s-%(levelname)s: %(message)s')
	handler.setFormatter(formatter)
	cls.log.addHandler(handler)
