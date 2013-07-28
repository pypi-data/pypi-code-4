# -*- coding: utf-8 -*-
from paste.script.templates import Template
from datetime import date
import shutil
import os

VERSION_FROM_BAZAAR = "bzr lp:openobject-server/7.0 openerp-server last:1"
VERSION_FROM_NIGHTLY = "nightly 7.0 latest"
ADDONS_FROM_BAZAAR = """bzr lp:openobject-addons/7.0 openerp-addons last:1
         bzr lp:openerp-web/7.0 openerp-web last:1 subdir=addons
         local addons/"""
ADDONS_FROM_NIGHTLY = "local addons/"


class Instance(Template):
    #egg_plugins = ['anybox_instance']
    summary = ("Template for creating an OpenERP Instance using buildout"
               "and an optional customer module")
    required_templates = []
    _template_dir = 'templates/instance'
    use_cheetah = True

    def pre(self, command, output_dir, vars):
        vars['year'] = str(date.today().year)

        # common questions
        loopvars = [
            ('author', 'author name', ''),
            ('author_email', 'author email', ''),
            ('description', 'small description', ''),
            ('depends', "comma-separated list of wanted OpenERP modules", ''),
        ]
        required = [
            'author',
            'author_email',
            'description',
        ]
        sep = '\n' + ' ' * 8
        while loopvars:
            var, question, default = loopvars[0]
            question = "Please enter the " + question + ' :'
            answer = command.challenge(question, default, True)
            if var not in required or answer != '':
                if var == 'depends' and answer:
                    answer = sep + sep.join([
                        "'" + x.strip() + "',"
                        for x in answer.split(',')
                        if x.strip() != 'base'])
                vars[var] = answer
                loopvars.pop(0)

        # bzr or nightly?
        answer = ''
        while answer.lower().strip() not in ('n', 'b'):
            question = "Use a [n]ightly release or [b]azaar development branches? n/b:"
            answer = command.challenge(question, '', True)
        if answer == 'b':
            vars['version_origin'] = VERSION_FROM_BAZAAR
            vars['addons_origin'] = ADDONS_FROM_BAZAAR
        elif answer == 'n':
            vars['version_origin'] = VERSION_FROM_NIGHTLY
            vars['addons_origin'] = ADDONS_FROM_NIGHTLY

        # local custom addon?
        answer = ''
        while answer.lower().strip() not in ('y', 'n'):
            question = "Do you want a local custom module? y/n:"
            answer = command.challenge(question, '', True)
        vars['custom_module'] = answer

    def post(self, command, output_dir, vars):
        # remove the custom module
        if vars['custom_module'] == 'n':
            module_path = os.path.join(output_dir, 'addons', vars['project'])
            if os.path.exists(module_path):
                shutil.rmtree(module_path)
            else:
                raise EnvironmentError('Something went wrong')

        print('\nYour instance is ready to build in the "%s" directory. '
              'Now you can run:\npython bootstrap.py\n./bin/buildout'
              '  # or: ./bin/buildout -c buildout.dev.cfg ' % vars['project'])
