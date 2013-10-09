import subprocess

class InvalidPathError(Exception): pass

def get_wallpaper():
	"""
	Return the current wallpaper's path.
	"""
	# Put together gsettings call
	cmd = [
		'gsettings', 
		'get', 
		'org.gnome.desktop.background', 
		'picture-uri'
	]
	# The call will return a string of the form "'file://PATH'\n", so we need
	# to clean it up
	uri = subprocess.check_output(cmd).strip().strip("'")
	# Get rid of the 'file://' prefix
	path = uri[len('file://'):]
	return path

def set_wallpaper(path):
	"""
	Set the system wallpaper to the given _full_ path.
	Throws: InvalidPathError
	"""
	# Validate path
	if len(path) == 0 or path[0] != '/': raise InvalidPathError()
	# Put together gsettings call
	cmd = [
		'gsettings', 
		'set', 
		'org.gnome.desktop.background', 
		'picture-uri', 
		'file://%s' % path
	]
	subprocess.call(cmd)
