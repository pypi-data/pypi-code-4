#!/usr/bin/env python

"""
filesystem template interpreter
"""

import inspect
import os
import re
import shutil
import subprocess
import sys
import tempfile
import urllib
# TODO: may have to use urllib2.urlopen to get reasonable timeouts

from ConfigParser import RawConfigParser
from optparse import OptionParser

# URL of -this file-
location = 'http://k0s.org/mozilla/hg/MakeItSo/raw-file/tip/makeitso/makeitso.py'

### import tempita

# URL of tempita
tempita_location = 'http://bitbucket.org/ianb/tempita/raw-file/tip/tempita/'

def cleanup():
    # remove temporary net module directory
    if 'tempdir' in globals():
        shutil.remove(tempdir)
try:
    import tempita
except ImportError:

    # Get tempita from the net
    # TODO: abstract this to get arbitrary modules from the net
    def getFiles(url, subdir, files):
        """
        fetch files from the internet
        - url : base url
        - subdirectory: to put things in
        - files : list of files to retrieve
        returns the location of a temporary directory
        """
        globals()['tempdir'] = tempfile.mkdtemp()
        os.mkdir(subdir)
        url = url.rstrip('/')
        for filename in files:
            f, headers = urllib.urlretrive('%s/%s' % (url, filename))
            content = file(f).read()
            outfile = os.path.join(globals()['tempdir'], subdir, filename)
            o = file(outfile, 'w')
            print >> o, content
        return globals()['tempdir']

    tempita_files = ['__init__.py', '_looper.py', 'compat3.py']

    try:
        t = getFiles(tempita_location, 'tempita', tempita_files)
        sys.path.append(t)
        import tempita
    except:
        cleanup()
        raise NotImplementedError('This should say something like youre not connected to the net')

# regular expressions for finding the shebang
shebang_re = '#!.*makeitso.*'
shebang_re = re.compile(shebang_re)

### URIs

def parent_uri(uri):
    """parent resource of a URI"""

    if '://' in uri:
        return uri.rsplit('/', 1)[0] + '/'
    else:
        here = os.path.dirname(os.path.abspath(uri))
        here = here.rstrip(os.path.sep) + os.path.sep
        return here

def basename(uri):
    """return the basename of a URI"""
    if '://' in uri:
        return uri.rsplit('/', 1)[1]
    else:
        return os.path.basename(uri)

def include(uri):
    f, headers = urllib.urlretrieve(uri) # XXX -> urllib2 for timeout
    return file(f).read()


### things that deal with variables

class MissingVariablesException(Exception):
    """exception for (non-interactive) missing variables"""
    def __init__(self, missing):
        self.missing = missing
        message = 'Missing variables: %s' % ', '.join(missing)
        Exception.__init__(self, message)

def get_missing(name_error):
    """
    This is a horrible hack because python doesn't do the proper thing
    via eval and return the name of the variable;  instead, it just gives
    you a message:
    >>> try:
    ...   eval('2*foo')
    ... except Exception, e:
    ...   pass
    """
    message = name_error.args[0]
    varname = message.split("'")[1]
    return varname

### template classes

class ContentTemplate(tempita.Template):
    """MakeItSo's extension of tempita's Template class"""

    defaults = {'include': include}

    def __init__(self, content, name=None, interactive=True, variables=None):

        # default variables
        self.defaults = self.__class__.defaults.copy()
        self.defaults.update(variables or {})

        # TODO: automagically tell if the program is interactive or not
        self.interactive = interactive

        tempita.Template.__init__(self, content, name=name)

    def get_variables(self, **variables):
        """the template's augmented variable set"""
        vars = self.defaults.copy()
        vars.update(variables)
        return vars

    def missing(self, **variables):
        """return additional variables needed"""
        vars = self.get_variables(**variables)
        missing = set([])
        while True:
            try:
                tempita.Template.substitute(self, **vars)
                return missing
            except NameError, e:
                missed = get_missing(e)
                missing.add(missed)
                vars[missed] = ''
        return missing

    def check_missing(self, vars):
        """
        check for missing variables and, if applicable,
        update them from the command line
        """
        missing = self.missing(**vars)
        if missing:
            if self.interactive:
                vars.update(self.read_variables(missing))
            else:
                raise MissingVariablesException(missing)

    def variables(self):
        """return the variables needed for a template"""
        return self.missing()

    def substitute(self, **variables):
        """interactive (for now) substitution"""
        vars = self.get_variables(**variables)
        self.check_missing(vars)
        return tempita.Template.substitute(self, **vars)

    def read_variables(self, variables):
        """read variables from stdin"""
        retval = {}
        for i in variables:
            print 'Enter %s: ' % i,
            retval[i] = raw_input()
        return retval


class URITemplate(ContentTemplate):
    """template for a file or URL"""

    def __init__(self, uri, interactive=True, variables=None):
        content = include(uri)

        # remove makeitso shebang if it has one
        if shebang_re.match(content):
            content = os.linesep.join(content.splitlines()[1:])

        variables = variables or {}
        if 'here' not in variables:
            variables['here'] = parent_uri(uri)
        # TODO: could add other metadata about the uri,
        # such as last modification time'

        ContentTemplate.__init__(self, content, name=uri,
                                 interactive=interactive,
                                 variables=variables)

    def substitute(self, variables, output=None):

        # interpolate
        content = ContentTemplate.substitute(self, **variables)

        # write output
        output = output or sys.stdout
        if isinstance(output, basestring):
            path = output
            if os.path.isdir(output):
                path = os.path.join(path, basename(self.name))
            f = file(path, 'w')
            print >> f, content
            f.close()
            try:
                os.chmod(path, os.stat(self.name).st_mode)
            except:
                pass
        else:
            # file handler
            print >> output, content


class DirectoryTemplate(ContentTemplate):
    """template for a directory structure"""

    def __init__(self, directory, interactive=True, variables=None):
        """
        - output : output directory; if None will render in place
        """
        assert os.path.isdir(directory)
        self.name = directory
        self.interactive = interactive
        self.defaults = ContentTemplate.defaults.copy()
        self.defaults.update(variables or {})

    def check_output(self, output):
        """
        checks output for validity
        """
        assert output # must provide output
        if os.path.exists(output):
            assert os.path.isdir(output), "%s: Must be a directory" % self.name

    def missing(self, **variables):
        vars = self.defaults.copy()
        vars.update(variables)
        missing = set([])
        for dirpath, dirnames, filenames in os.walk(self.name):

            # find variables from directory names
            for d in dirnames:
                missed = ContentTemplate(d).missing(**vars)
                missing.update(missed)
                variables.update(dict([(i, '') for i in missed]))

            # find variables from files
            for f in filenames:
                missed = ContentTemplate(f).missing(**vars)
                missing.update(missed)
                variables.update(dict([(i, '') for i in missed]))

                path = os.path.join(dirpath, f)
                template = URITemplate(path, interactive=self.interactive)
                missed = template.missing(**vars)
                missing.update(missed)
                variables.update(dict([(i, '') for i in missed]))

        return missing

    def substitute(self, variables, output):
        self.check_output(output)
        vars = self.get_variables(**variables)
        self.check_missing(vars)

        # TODO: do this with recursion instead of os.walk so that
        # per-directory control may be asserted

        # make output directory if necessary
        if output and not os.path.exists(output):
            os.makedirs(output)

        for dirname, dirnames, filenames in os.walk(self.name):

            # interpolate directory names
            for d in dirnames:
                path = os.path.join(dirname, d)
                interpolated = ContentTemplate(path).substitute(**vars)
                target = os.path.join(output, interpolated.split(self.name, 1)[-1].strip(os.path.sep))

                if os.path.exists(target):
                    # ensure its a directory
                    # TODO: check this first before interpolation is in progress
                    assert os.path.isdir(target), "Can't substitute a directory on top of the file"
                else:
                    os.makedirs(target)

            # interpolate files
            for filename in filenames:

                # interpolate filenames
                path = os.path.join(dirname, filename)
                interpolated = ContentTemplate(path).substitute(**vars)
                target = os.path.join(output, interpolated.split(self.name, 1)[-1].strip(os.path.sep))

                # interpolate their contents
                if os.path.exists(target):
                    # ensure its a directory
                    assert os.path.isfile(target), "Can't substitute a file on top of a directory"
                template = URITemplate(path, interactive=False)
                template.substitute(vars, target)


class PolyTemplate(ContentTemplate):
    """aggregate templates"""

    def __init__(self, templates, interactive=True, variables=None):
        self.interactive = interactive
        self.templates = []
        entry_points = get_entry_points()
        for template in templates:
            if isinstance(template, basestring):
                # TODO: check if the template is a [e.g] PasteScript.template entry point
                if os.path.isdir(template):
                    self.templates.append(DirectoryTemplate(template, interactive=self.interactive, variables=variables))
                elif not os.path.exists(template) and template in entry_points:
                    self.templates.append(entry_points[template](interactive=interactive, variables=variables))
                else:
                    self.templates.append(URITemplate(template, interactive=self.interactive, variables=variables))
            else:
                # assume the template is an object that conforms to the API
                self.templates.append(template)

    def get_variables(self, **variables):
        vars = variables.copy()
        for template in self.templates:
            vars.update(template.get_variables())
        return vars

    def missing(self, **variables):
        vars = variables.copy()
        missing = set([])
        for template in self.templates:
            missed = template.missing(**vars)
            missing.update(missed)
            vars.update(dict([(i, '') for i in missed]))
        return missing

    def check_output(self, output):
        if output and isinstance(output, basestring) and os.path.exists(output) and len(self.templates) > 1:
            assert os.path.isdir(output), "Must specify a directory for multiple templates"
        for template in self.templates:
            if hasattr(template, 'check_output'):
                template.check_output(output)

    def substitute(self, variables, output=None):

        # determine where the hell to put these things
        self.check_output(output)

        # get the variables
        vars = self.get_variables(**variables)
        self.check_missing(vars)

        # make the output directory if multiple templates
        if output and len(self.templates) > 1 and not os.path.exists(output):
            os.makedirs(output)

        # do the substitution
        for template in self.templates:
            template.substitute(vars, output)

### command line interface

def read_config(config_files, templates=()):
    """read variables from a set of .ini files"""
    retval = {}
    parser = RawConfigParser()
    parser.read(config_files)
    retval.update(dict(parser.items('DEFAULT')))
    for template in templates:
        if template in parser.sections():
            retval.update(dict(parser.items(template)))
    return retval

def invocation(url, **variables):
    """returns a string appropriate for TTW invocation"""
    variables_string = ' '.join(['%s=%s' % (i,j) for i,j in variables.items()])
    return 'python <(curl %s) %s %s' % (location, url, variables_string)

def main(args=sys.argv[1:]):

    # create option parser
    usage = '%prog [options] template <template> <...>'
    parser = OptionParser(usage, description=__doc__)

    # find dotfile
    dotfile = None
    if 'HOME' in os.environ:
        dotfile = os.path.join(os.environ['HOME'], '.makeitso')
        if not (os.path.exists(dotfile) and os.path.isfile(dotfile)):
            dotfile = None

    parser.add_option('-[', '--start-braces', dest='start_braces',
                      help='starting delimeter')
    parser.add_option('-]', '--end-braces', dest='end_braces',
                      help='starting delimeter')

    # options about where to put things
    parser.add_option('-o', '--output', dest='output',
                      help='where to put the output (filename or directory)')

    # options for (.ini) variables
    parser.add_option('-c', '--config', dest='config',
                       default=[], action='append',
                       help='.ini config files to read variables from')
    if dotfile:
        parser.add_option('--no-defaults', dest='use_defaults',
                          default=True, action='store_false',
                          help="don't read ~/.makeitso")

    # TODO
#     parser.add_option('-u', '--update', dest='update',
#                       help="update the specified .ini file for variables read from this run")
#     parser.add_option('-U', '--Update', dest='Update',
#                       help="same as -u, but update the global [DEFAULTS] section")
#     parser.add_option('--dry-run', dest='dry_run',
#                       default=False, action='store_true',
#                       help="don't actually do the substitution but do everything else")

    # options for getting information
    parser.add_option('--commandline', dest='commandline',
                      action='store_true', default=False,
                      help="print the commandline to invoke this script TTW")
    parser.add_option('--variables', dest='variables',
                      action='store_true', default=False,
                      help='print the variables in a template')
    entry_points = get_entry_points()
    if entry_points:
        parser.add_option('--list-templates', dest='list_templates',
                          action='store_true', default=False,
                          help="list installed MakeItSo! templates")

    options, args = parser.parse_args(args)

    # list the templates
    if entry_points and options.list_templates:
        for key in sorted(entry_points.keys()):
            template_class = entry_points[key]
            description = getattr(template_class, 'description', '')
            description = description or getattr(template_class, '__doc__', '')
            description = description.strip()
            print key + ': ' + description
        return

    # print the variables for the templates
    if options.variables:

        # makes no sense without a template
        if not args:
            parser.print_usage()
            parser.exit()

        # find all variables
        template = PolyTemplate(templates=args)
        variables = template.variables()

        # print them
        for variable in sorted(variables):
            print variable
        return

    # template variables
    variables = {}
    _args = []

    # read variables from configuration
    config_files = options.config
    if dotfile and options.use_defaults:
        config_files.insert(0, dotfile)
    if config_files:
        variables.update(read_config(config_files))

    # override with variables from the command line
    _variables = {}
    for arg in args:
        if '=' in arg:
            key, value = arg.split('=')
            _variables[key] = value
        else:
            _args.append(arg)
    args = _args
    variables.update(_variables)

    # print TTW commandline for invocation
    if options.commandline:
        if args:
            for arg in args:
                print invocation(arg, **variables)
        else:
            print invocation('[URI]', **variables)
        return


    # get the content
    if args:
        template = PolyTemplate(templates=args,
                                variables=variables)
        template.substitute({}, output=options.output)
    else:
        template = ContentTemplate(sys.stdin.read(), variables=variables)
        print template.substitute()

    # cleanup
    cleanup()

if __name__ == '__main__':
    main()


# get templates from pkg_resources
# (MakeItSo! and [TODO] pastescript templates)
# this should go last to ensure the module is wholly loaded [?]
def get_entry_points():
    retval = {}
    try:
        from pkg_resources import iter_entry_points
        for i in iter_entry_points('makeitso.templates'):
            try:
                retval[i.name] = i.load()
            except:
                continue

    except ImportError:
        return retval
    return retval
