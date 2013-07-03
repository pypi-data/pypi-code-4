# -*- coding: utf-8 -*-
"""Recipe logger"""

import os
import logging

import zc.buildout
import zc.recipe.egg

from .config import INITIALIZATION, SCRIPT_ARGUMENTS, DEFAULT_OPTIONS

logger = logging.getLogger(__name__)


def create_script(**kwargs):
    """ Create a script. """
    script = zc.buildout.easy_install.scripts(
        kwargs.get('reqs'),
        kwargs.get('working_set'),
        kwargs.get('executable'), kwargs.get('dest'),
        arguments=kwargs.get('script_arguments'),
        initialization=kwargs.get('initialization'))
    return script


class Recipe(object):
    """zc.buildout recipe"""

    def __init__(self, buildout, name, options):
        self.buildout, self.name, self.options = buildout, name, options
        self.egg = zc.recipe.egg.Egg(buildout, self.options['recipe'], options)

    def getScriptOptions(self):
        # work with a copy of the options, for safety.
        opts = self.options.copy()
        for option, value in DEFAULT_OPTIONS.items():
            # initialize args
            opts.setdefault(option, value)
        opts['main_dir'] = os.path.join(
            self.buildout['buildout']['parts-directory'], self.name)
        opts['storage_dir'] = os.path.join(opts['main_dir'], 'storage')
        return opts

    def install(self):
        """Installer"""
        # set up working set which helps to extend sys.path
        extra_eggs = self.options.get('eggs', '').split()
        orig_distributions, working_set = self.egg.working_set(
            extra_eggs + ['collective.recipe.logger', 'zc.buildout', 'zc.recipe.egg']
        )

        # prepare arguments for script
        script_options = self.getScriptOptions()

        # create main directory (script directory).
        # pidfile, error and output will be saved there.
        os.mkdir(script_options['main_dir'])
        # subfolder to main_dir. Logs will be saved there
        os.mkdir(script_options['storage_dir'])

        script_arguments = SCRIPT_ARGUMENTS % script_options

        bin_dir = self.buildout['buildout']['bin-directory']
        buildout_dir = os.path.join(bin_dir, os.path.pardir)

        python = self.buildout['buildout']['python']
        executable = self.buildout[python]['executable']
        creation_args = dict(
            dest=bin_dir,
            working_set=working_set,
            executable=executable,
            initialization=INITIALIZATION,
            script_arguments=script_arguments)


        # create logger (script)
        reqs = [(self.name,
                 'collective.recipe.logger.main',
                 'logger_main')]
        creation_args['reqs'] = reqs
        # list of generated files/directories/scripts
        generated = create_script(**creation_args)
        generated.append(script_options['main_dir'])
        generated.append(script_options['storage_dir'])

        return generated


    def update(self):
        """Updater"""
        pass

