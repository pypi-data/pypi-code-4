from os import path, getenv, listdir, remove, makedirs, rmdir
import requests
import subprocess
from models import Script, Gist

def get_scripts(global_dir=False):
	bam_dir = get_bam_dir(global_dir)
	if not path.exists(bam_dir):
		return []
	scripts = []
	for item in listdir(bam_dir):
		if path.isdir( path.join(bam_dir, item) ):
			for script_name in listdir( path.join(bam_dir, item) ):
				if path.isfile( path.join(bam_dir, item, script_name) ):
					script = Script( script_name, path.join(bam_dir, item, script_name), '%s/%s' % (item, script_name) )
					scripts.append(script)
		else:
			script = Script(item, path.join(bam_dir, item))
			scripts.append(script)

	return scripts

def get_script(name, global_dir=False):
	for script in get_scripts(global_dir):
		if script.name == name:
			return script
	return None

def add_script(origin=None, file_path=None, name=None, script=None, global_dir=False):
	bam_dir = get_bam_dir(global_dir)
	script = Script()
	if origin:
		script.origin = origin
		script.name = origin.split('/')[1]
		script.path = path.join(bam_dir, origin)
		if get_script(script.name, global_dir):
			print "Script with this name already exists."
			return None
		gist = get_gist(script.origin)
		if not gist:
			print "Unable to find gist."
			return None
		script_contents = requests.get(gist.raw_url)
		if not script_contents:
			print "Found gist, but unable to download script contents."
			return None
		if not path.exists(path.dirname(script.path)):
			makedirs(path.dirname(script.path))
		f = open(script.path, 'w')
		f.write(script_contents.text)
		f.close
		return script

def rm_script(name, global_dir=False):
	script = get_script(name, global_dir)
	if not script:
		print "No script found with that name."
		return -1
	remove(script.path)
	try:
		rmdir( path.dirname(script.path) )
	except OSError:
		pass
	return 0

def ls_scripts(global_dir=False):
	scripts = get_scripts(global_dir)
	if scripts:
		print "name\t\torigin"
		print "-----------------------------------------"
		for script in scripts:
			print "%s\t\t%s" % (script.name, script.origin if script.origin else '')
	return 0

def run_script(name, global_dir=False):
	script = get_script(name)
	if not script:
		print "No script found with that name."
		return -1
	#print script.path
	return subprocess.call('source %s' % script.path, shell=True)

def get_gists(user):
	api_response = requests.get('https://api.github.com/users/%s/gists' % user)
	if not api_response:
		print "A GitHub user with that name does not exist."
		return []
	gists = []
	for item in api_response.json():
		name, gist_file = item['files'].popitem()
		gist = Gist(item['id'], gist_file['raw_url'])
		if name != "gistfile1.txt":
			gist.name = name
		gists.append(gist)
	return gists

def get_gist(slug):
	user, name = slug.split('/')
	for gist in get_gists(user):
		if gist.name == name or gist.id == name:
			return gist
	return None

def get_bam_dir(global_dir=False):
	if global_dir:
		return path.join( path.expanduser('~'), '.bam' )
	return path.join( getenv('VIRTUAL_ENV', path.expanduser('~')), '.bam' )
