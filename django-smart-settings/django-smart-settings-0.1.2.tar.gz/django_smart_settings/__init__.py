import sys
import socket
import getpass

def _load_settings_from_module(module_name, destination):
	module = __import__(module_name, globals(), locals(),['*'])
	for name in dir(module):
		if name.isupper():
			destination[name] = getattr(module, name)

def _import_default_settings(destination, module):
	try:
		_load_settings_from_module(module, destination)
	except ImportError:
		import sys, traceback
		sys.stderr.write("Error loading default settings\n\n")
		traceback.print_exc()
		raise

def _import_machine_settings(destination):
	try:
		_load_settings_from_module(socket.gethostname(), destination)
	except ImportError as e:
		if e.message == "No module named %s" % socket.gethostname():
			pass
		else:
			raise

def _import_user_settings(destination):
	try:
		_load_settings_from_module(getpass.getuser(), destination)
	except ImportError as e:
		if e.message == "No module named %s" % getpass.getuser():
			pass
		else:
			raise

def _import_variable_settings(destination):
	try:
		import os
		if os.environ.get('DJANGO_ENV'):
			_load_settings_from_module(os.environ['DJANGO_ENV'], destination)
	except ImportError:
		import sys, traceback
		sys.stderr.write("Error loading settings from DJANGO_ENV variable:\n\n")
		traceback.print_exc()
		raise

def configure(destination, module='default'):
	_import_default_settings(destination, module)
	_import_machine_settings(destination)
	_import_user_settings(destination)
	_import_variable_settings(destination)