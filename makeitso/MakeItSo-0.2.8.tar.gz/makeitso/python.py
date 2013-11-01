#!/usr/bin/env python

"""
python package templates for makeitso

Several components are included.
[TODO] You may use these subtemplates in any combination.

* README.txt : a README in restructured text
* examples : examples for your package
* setup.py : setup utility for the full package
* ./main.py : CLI handler for your webapp
* ./model.py : model of a persisted object
* ./template.py : a MakeItSo template for project creation
* ./tests : doctest suite for the package
* ./web.py : a webob web handler
"""

# TODO: console_scripts for all of these

import os
import shutil
import sys
from cli import MakeItSoCLI
from makeitso import ContentTemplate
from optparse import OptionParser
from template import MakeItSoTemplate
from template import Variable


class PythonTemplate(MakeItSoTemplate):
  """abstract base class for python-type templates"""
  vars = [Variable('description'),
          Variable('author', 'author of the package'),
          Variable('email', "author's email"),
          Variable('url', 'project url'),
          Variable('repo', 'project repository'),
          ]

  def output2name(self, path):
    return os.path.splitext(os.path.basename(path.rstrip(os.path.sep)))[0]


class PythonScriptTemplate(PythonTemplate):
  """template for a single python script"""
  templates = [('python_package', '{{package}}', '{{main}}.py')]
  vars = [Variable('description')]


class PythonModuleTemplate(PythonTemplate):
  """single module python package"""
  # TODO: this should use the same files as PythonPackageTemplate
  templates = ['python_module',
               ('python_package', '{{package}}', '{{main}}.py')]
  vars = [Variable('description')]
  look = False

  def pre(self, variables, output):
    variables['project'] = variables['module'] = variables['main'] = self.output2name(output)

  def post(self, variables, output):
    shutil.move(os.path.join(output, '{{main.py}}'),
                os.path.join(output, variables['main']))

class PythonPackageTemplate(PythonTemplate):
  """
  python package template
  """
  name = 'python-package'
  templates = ['python_package']
  vars = [Variable('description'),
          Variable('author', 'author of the package'),
          Variable('email', "author's email"),
          Variable('url', 'project url'),
          Variable('repo', 'project repository'),
          ]
  look = False

  # things that go in setup.py
  dependencies = {'web.py': ['webob'],
                  'template.py': ['MakeItSo']}
  console_scripts = {'main.py': '{{project}} = {{package}}.{{main}}:main',
                     'template.py': '{{package}}-template = {{package}}.template:main'
                     }

  def __init__(self, **kw):
    MakeItSoTemplate.__init__(self, **kw)

    # TODO: get the templates you actually care about [maybe from the CLI?]

  def pre(self, variables, output):
    """
    sanitize some variables
    """

    # get project from output directory
    variables['project'] = self.output2name(output)

    # get package name from project
    # XXX could have looser restrictions with transforms
    assert variables['project'].isalnum(), 'Project name must be just letters, you gave %s' % variables['project']
    variables['package'] = variables['project'].lower()

    # name of CLI main file
    variables['main'] = 'main'

    # dependencies
    dependencies = set([])
    for template, dependency in self.dependencies.items():
      dependencies.update(dependency)
    dependencies = list(dependencies)
    variables['dependencies'] = dependencies

    # console_scripts
    console_scripts = []
    for template, console_script in self.console_scripts.items():
      console_scripts.append(console_script)
    if console_scripts:
      s = 'setup(' # placeholder string
      script_strings = ['[console_scripts]']
      for console_script in console_scripts:
        template = ContentTemplate(console_script)
        output = template.substitute(project=variables['project'])
        script_strings.append(output)
      variables['console_scripts'] = '\n'.join([' ' * len(s) + i
                                                for i in script_strings])
    else:
      variables['console_scripts'] = ''


class PythonPackageCLI(MakeItSoCLI):
  """
  CLI front end for the python package template
  """
  usage = '%prog [options] project'

def main(args=sys.argv[1:]):
  cli = PythonPackageCLI(PythonPackageTemplate)
  cli(*args)

if __name__ == '__main__':
  main()
