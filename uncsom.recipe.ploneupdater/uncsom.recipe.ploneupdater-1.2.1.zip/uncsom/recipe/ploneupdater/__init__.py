from os.path import join as pathjoin
from os.path import exists as pathexists
from os.path import dirname
from os.path import basename
from os import chmod

# import zc.buildout
from sys import platform

template = """#!%(executable)s
import subprocess

%(zeo-start)s

cmd = "%(instance-script)s stop"
subprocess.call(cmd.split())

cmd = "%(instance-script)s run %(script)s %(args)s"
subprocess.call(cmd.split())

%(zeo-stop)s
"""

zeo_start_template = """zeo_start = "%s start" % zeo_cmd
subprocess.call(zeo_start.split())"""

zeo_stop_template = """zeo_stop = "%s stop" % zeo_cmd
subprocess.call(zeo_stop.split())"""


class Recipe(object):
    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options
        self.options['bin-directory'] = \
            self.buildout['buildout']['bin-directory']
        self.options['bin_dir'] = self.options['bin-directory']
        self.options.setdefault('admin-user', 'admin')
        self.options.setdefault('zope_part', 'instance')
        self.options.setdefault('zeo_part', '')
        self.options.setdefault('zeo-start', '')
        self.options.setdefault('zeo-stop', '')

        python = buildout['buildout']['python']
        self.options['executable'] = buildout[python]['executable']

        self.options['script'] = pathjoin(dirname(__file__), 'ploneupdater.py')

        zeo_recipes = ('plone.recipe.zeoserver', 'plone.recipe.zope2zeoserver')

        zope_recipes = ('plone.recipe.zope2instance')

        for id in self.buildout.keys():
            recipe = self.buildout[id].get('recipe', None)
            if recipe and recipe in zeo_recipes:
                self.options['zeo_part'] = id
                break

        for id in self.buildout.keys():
            recipe = self.buildout[id].get('recipe', None)
            if recipe and recipe in zope_recipes:
                self.options['zope_part'] = id
                break

        is_win = platform[:3].lower() == "win"

        instance = buildout[self.options['zope_part']]
        instance_home = instance['location']
        instance_script = basename(instance_home)
        if is_win:
            instance_script = "%s.exe" % instance_script
        self.options['instance-script'] = instance_script

        if self.options['zeo_part']:
            if is_win:
                if pathexists(pathjoin(self.options['bin-directory'],
                              'zeoservice.exe')):
                    zeo_script = 'zeoservice.exe'
                else:
                    zeo_script = "%s_service.exe" % self.options['zeo_part']
            else:
                zeo_home = buildout[self.options['zeo_part']]['location']
                zeo_script = basename(zeo_home)
            self.options['zeo-script'] = zeo_script
            self.options['zeo-start'] = zeo_start_template % self.options
            self.options['zeo-stop'] = zeo_stop_template % self.options

        self.options['args'] = self.createArgs()

    def install(self):
        script_path = pathjoin(self.options['bin-directory'], self.name)
        open(script_path, 'w+').write(template % self.options)

        chmod(script_path, 0700)

        return tuple()

    def update(self):
        self.install()

    def createArgs(self):
        """Helper method to create an argument list
        """
        args = []
        args.append("--admin-user=%s" % self.options['admin-user'])

        return " ".join(args)
