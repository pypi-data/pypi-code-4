from paste.script.templates import Template
import datetime
import os
import ConfigParser
import re


class Module(Template):
    egg_plugins = ['anybox_openerp']
    summary = 'Template for creating an OpenERP python file'
    required_templates = []
    _template_dir = 'templates/module'
    use_cheetah = True

    def pre(self, command, output_dir, vars):
        def get_conf(conffile, section, option):
            author = ""
            author_email = ""
            val = ""
            p = ConfigParser.ConfigParser()
            try:
                p.read([conffile])
                for o, v in p.items(section):
                    if o == option:
                        val = v
                if val:
                    regex = re.compile('(.*) <(.*)>')
                    author, author_email = regex.findall(val)[0]
            except Exception, e:
                print e

            return author, author_email

        hgfile = os.path.expanduser("~/.hgrc")
        bzrfile = os.path.expanduser("~/.bazaar/bazaar.conf")
        if os.path.exists(hgfile):
            author, author_email = get_conf(hgfile, 'ui', 'username')
        elif os.path.exists(bzrfile):
            author, author_email = get_conf(bzrfile, 'DEFAULT', 'email')

        loopvars = [
            ('description', 'Small description', ''),
            ('author', 'Author name', author),
            ('author_email', 'Author email', author_email),
            ('name', 'Module Name', vars['project'].replace('_', ' ')),
            ('version', 'Module version', '0.1'),
            ('category', 'Module category',  vars['project'].replace('_', ' ')),
            ('company', 'Author Company', "Anybox"),
            ('website', 'Website', "http://anybox.fr"),
            ('depends', 'List of OpenERP module dependencies (separated by ,)', "base"),
            ('app', 'Is the module an application? (True/False)', "False"),
            ('active', 'Should the module be installed automatically? (True/False)', "False"),
        ]
        counter = 0
        vars['year'] = str(datetime.date.today().year)
        while counter < len(loopvars):
            field, question, default = loopvars[counter]
            if field in ('active', 'application'):
                question=command.challenge(question + ' :', default, True)
                if question not in ('True', 'False'):
                    continue
            else:
                question=command.challenge('Please Enter ' + question + ' :', default, True)
            if question != '':
                if field == 'depends':
                    question =  ','.join(["'" + x.strip() + "'" for x in question.split(',')])
                vars[field] = question
                counter += 1
