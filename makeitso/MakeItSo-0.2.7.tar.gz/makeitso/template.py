"""
basic API template class
"""

import os
import sys
from makeitso import ContentTemplate
from makeitso import PolyTemplate

class Undefined(object):
    """marker class for variables"""
    def __nonzero__(self):
        return False
Undefined = Undefined() # singleton


class Variable(object):
    """variable object for MakeItSo templates"""

    def __init__(self, name, description=None, default=Undefined,
                 cast=None):
        self.name = name
        self.default = default
        self.description = description

        # TODO (maybe): get cast from default variable type if not None
        self.cast = cast

        self._set = False

    def copy(self):
        """returns a copy of the variable"""
        return Variable(self.name, self.description, self.default, self.cast)

    def set(self, value):
        if self.cast:
            self.value = self.cast(value)
        else:
            self.value = value
        self._set = True
        return self.value

    def isset(self):
        """whether the variable has been set or not"""
        return self._set

    def read(self, fd=sys.stdout):
        """prompt and read the variable from stdin"""
        fd.write(self.display())
        return self.set(raw_input())

    def display(self):
        description = self.description or self.name
        if self.default:
            return 'Enter %s [DEFAULT: %s]: ' % (description, repr(self.default))
        else:
            return 'Enter %s: ' % description

    def __repr__(self):
        return "Variable(name='%s')" % self.name

def assemble(*args):
    names = set()
    retval = []
    for arg in args:
        if issubclass(arg, MakeItSoTemplate):
            arg = arg.vars
        for variable in arg:
            if variable.name in names:
                continue
            retval.append(variable.copy())
            names.add(variable.name)
    return retval

class MakeItSoTemplate(ContentTemplate):
    """API template for MakeItSo"""

    # name of the template
    name = ''

    # description of the template
    description = ''

    # templates to interpolate
    # paths are relative to __file__ unless absolute or URIs
    templates = []

    # variables
    vars = []

    # inspect the templates for more variables
    look = False

    def __init__(self, interactive=True, usedefaults=True, variables=None):
        """
        - output : output file or directory
        - interactive : whether tointeractively get variables
        - usedefaults : try to use the default values if not specified
        """

        # boilerplate
        variables = variables or {}
        if not self.description and hasattr(self, '__doc__'):
            self.description = self.__doc__
        self.interactive = interactive
        _file = sys.modules[self.__class__.__module__].__file__
        self.location = os.path.dirname(os.path.abspath(_file))
        self.defaults = variables.copy()
        self.usedefaults = usedefaults

        # make a dictionary of the variables for lookup convenience
        self.vardict = {}
        for i in self.vars:
            self.vardict[i.name] = i

        # ensure all of these templates exist
        self._templates = []
        for template in self.templates:
            if not isinstance(template, basestring):
                template = os.path.join(*template)
            if template.startswith('http://') or template.startswith('https://'):
                self._templates.append(template)
                continue
            if os.path.isabs(template):
                path = template
            else:
                path = os.path.join(self.location, template)
            assert os.path.exists(path), "%s does not exist" % path
            self._templates.append(path)

    @classmethod
    def get_description(cls):
        if hasattr(cls, 'description'):
            if cls.description:
                return cls.description
        if hasattr(cls, '__doc__'):
            return cls.__doc__

    def get_variables(self, **variables):
        # XXX could do this in the ctor
        vars = ContentTemplate.get_variables(self, **variables)
        if self.usedefaults:
            for variable in self.vars:
                if variable.name in vars:
                    continue
                if variable.default is not Undefined:
                    vars[variable.name] = variable.default
        return vars

    def missing(self, **variables):

        # boilerplate
        vars = self.get_variables(**variables)
        missing = set([])

        # get known needed variables
        for var in self.vars:
            if var.name not in vars:
                if var.default is Undefined:
                    missing.add(var.name)
                    continue
                if (not self.usedefaults) and (not var.isset()):
                    missing.add(var.name)

        # scan templates for other variables
        if self.look:
            template = PolyTemplate(self._templates,
                                    interactive=False,
                                    variables=vars)
            missing.update(template.missing())

        return missing

    def pre(self, variables, output):
        """do stuff before interpolation"""

    def substitute(self, variables, output=None):
        """do the substitution"""

        # get the variables
        vars = self.get_variables(**variables)
        self.pre(vars, output)
        self.check_missing(vars)

        # do the substitution
        template = PolyTemplate(self._templates,
                                interactive=self.interactive,
                                variables=vars)
        template.check_output(output)
        template.substitute({}, output)

        # do whatever you need to do afterwards
        self.post(vars, output)

    def post(self, variables, output):
        """do stuff after interpolation"""

    def read_variables(self, variables):
        """read variables from stdin"""
        retval = {}
        for i in variables:
            if i in self.vardict:
                value = self.vardict[i].read()
                retval[i] = value
            else:
                retval.update(ContentTemplate.read_variables(self, (i,)))
        return retval

class PasteScriptTemplate(MakeItSoTemplate):
    """template for backwards compatability with PasteScript"""
