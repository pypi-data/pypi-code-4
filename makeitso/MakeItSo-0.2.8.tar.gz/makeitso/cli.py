"""
command line parser for MakeItSo
"""

from template import Undefined
from optparse import OptionParser

class MakeItSoCLI(object):
  """command line interface to a makeitso template"""
  
  def __init__(self, template_class):
    self.template_class = template_class

  def parser(self):
    """
    return a command line parser for the template
    """
    usage = getattr(self, 'usage', '%prog [options] output')
    description = self.template_class.get_description()
    parser = OptionParser(usage=usage, description=description)

    # add the variables as options
    for variable in self.template_class.vars:
      description = variable.description
      if (variable.default is not None) and (variable.default is not Undefined) and description is not None:
        description += ' [DEFAULT: %s]' % variable.default
      parser.add_option('--%s' % variable.name, dest=variable.name,
                        default=variable.default,
                        help=description)
    return parser

  def get_variables(self, options):
    """
    return variables from (parsed) options
    """
    return dict([(key, value)
                 for key, value in options.__dict__.items()
                 if (not key.startswith('_')) and (value is not Undefined)])

  def parse(self, args=None, parser=None, options=None):

    # parse the command line
    if not parser or not options:
      parser = self.parser()
      options, args = parser.parse_args(args=args)

    # ensure output is given
    if len(args) != 1:
      parser.error("Please specify a single output destination")

    # template variables
    variables = self.get_variables(options)
    
    # return the variables and the output
    return variables, args[0]
    
  def __call__(self, *args):
    variables, output = self.parse(list(args))
    template = self.template_class(variables=variables)
    template.substitute({}, output=output)
