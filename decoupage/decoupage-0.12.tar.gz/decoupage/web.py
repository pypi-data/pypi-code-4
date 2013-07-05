"""
decoupage: a view with webob to index and serve static content
"""

# TODO:
# files like `index.ini`
# -> http://k0s.org/portfolio/ideas/#index.ini#
#
# oops. Handle it better
# - either # is a magic hide character
# - or you urlescape that guy

import os
import sys

from contenttransformer.app import FileTypeTransformer
from contenttransformer.app import transformers
from datetime import datetime
from formatters import formatters
from genshi.builder import Markup
from genshi.template import TemplateLoader
from genshi.template.base import TemplateError
from genshi.template.base import TemplateSyntaxError
from martini.config import ConfigMunger
from paste.fileapp import FileApp
from pkg_resources import iter_entry_points
from pkg_resources import load_entry_point
from pkg_resources import resource_filename
from webob import Request, Response, exc

transformers = transformers()

class Decoupage(object):

    ### class level variables
    defaults = { 'auto_reload': 'False',
                 'configuration': None,
                 'directory': None, # directory to serve
                 'cascade': 'True', # whether to cascade configuration
                 'template': 'index.html', # XXX see below
                 'template_directories': '' # list of directories to look for templates
                 }

    def __init__(self, **kw):

        # set defaults from app configuration
        for key in self.defaults:
            setattr(self, key, kw.get(key, self.defaults[key]))

        # configure defaults
        assert self.directory, "Decoupage: directory not specified"
        self.auto_reload = self.auto_reload.lower() == 'true'
        self.cascade = self.cascade.lower() == 'true'
        self.directory = self.directory.rstrip(os.path.sep)
        assert os.path.isdir(self.directory), "'%s' is not a directory" % self.directory
        self.template_directories = self.template_directories.split() # no spaces in directory names, for now

        for directory in self.template_directories:
            assert os.path.isdir(directory), "Decoupage template directory %s does not exist!" % directory

        # static file server
        self.fileserver = FileApp

        # pluggable formats
        s = 'format.'
        _format_args = [ (i.split(s, 1)[-1], j) for i, j in kw.items()
                         if i.startswith(s) ]
        format_args = {}
        for i, j in _format_args:
            assert i.count('.') == 1, 'Illegal string or something'
            format_name, var_name = i.split('.')
            format_args.setdefault(format_name, {})[var_name] = j
        self.formats = {}
        for _format in iter_entry_points('decoupage.formats'):
            try:
                _cls = _format.load()
                _instance = _cls(self, **format_args.get(_format.name, {}))
            except Exception, e:
                # record the error, but persist
                print >> sys.stderr, "Couldn't load format: %s" % _format
                print >> sys.stderr, e
                continue
            self.formats[_format.name] = _instance

        # pluggable index data formatters
        self.formatters = {}
        for formatter in iter_entry_points('decoupage.formatters'):
            try:
                _formatter = formatter.load()
                template_dir = resource_filename(formatter.module_name, 'templates')
                if template_dir not in self.template_directories and os.path.isdir(template_dir):
                    self.template_directories.append(template_dir)
            except Exception, e:
                # record the error, but persist
                print >> sys.stderr, "Couldn't load formatter: %s" % formatter
                print >> sys.stderr, e
                continue
            self.formatters[formatter.name] = _formatter

        # template loader
        self.loader = TemplateLoader(self.template_directories,
                                     variable_lookup="lenient",
                                     auto_reload=self.auto_reload)



    ### methods dealing with HTTP

    def __call__(self, environ, start_response):

        # boilerplate: request and filename
        request = Request(environ)
        filename = request.path_info.strip('/')
        path = os.path.join(self.directory, filename)

        # check to see what we have to serve
        if os.path.exists(path):

            if os.path.isdir(path):
                # serve an index
                if request.path_info.endswith('/'):
                    res = self.get(request)
                else:
                    res = exc.HTTPMovedPermanently(add_slash=True)
                return res(environ, start_response)

            else:
                # serve a file
                conf = self.conf(request.path_info.rsplit('/',1)[0])
                if '/transformer' in conf:
                    args = [i.split('=', 1) for i in conf['/transformer'].split(',') if '=' in i]
                    kwargs = {}
                    for i in conf:
                        if i.startswith('/'):
                            name = i[1:]
                            if name in transformers:
                                kwargs[name] = dict([j.split('=', 1) for j in conf[i].split(',') if '=' in j])
                    fileserver = FileTypeTransformer(*args, **kwargs)
                else:
                    fileserver = self.fileserver

                fileserver = fileserver(path)
                return fileserver(environ, start_response)
        else:
            # file does not exist
            conf = self.conf('/')
            data = dict(request=request,
                        title="Not Found")
            template = self.loader.load('HTTPNotFound.html')
            body = template.generate(**data).render('html', doctype='html')
            response = Response(content_type='text/html', body=body, status=404)
            return response(environ, start_response)


    def get(self, request):
        """
        return response to a GET requst
        """

        # ensure a sane path
        path = request.path_info.strip('/')
        directory = os.path.join(self.directory, path)
        path = '/%s' % path

        # get the configuraton
        conf = self.conf(path)

        ### build data dictionary
        # TODO: separate these out into several formatters
        files = self.filedata(path, directory, conf)
        data = {'path': path, 'files': files, 'request': request }

        # add a function to get the path to files
        data['filepath'] = lambda *segments: os.path.join(*([directory] + list(segments)))

        # defaults
        data['directory'] = directory
        data['css'] = ()
        data['scripts'] = ()

        # apply formatters
        # XXX this should be cached if not self.auto_reload
        if '/formatters' in conf:
            # ordered list of formatters to be applied first
            formatters = [ i for i in conf['/formatters'].split()
                           if i in self.formatters ]
        else:
            formatters = []
        for key in conf:
            if key.startswith('/'):
                key = key[1:]
                if key in self.formatters and key not in formatters:
                    formatters.append(key)
        for name in formatters:
            formatter = self.formatters[name](conf.get('/%s' % name, ''))
            formatter(request, data)

        # return an alternate format if specified
        # decoupage.formats should return a 2-tuple:
        # (content_type, body)
        if 'format' in request.GET:
            format_name = request.GET['format']
            if format_name in self.formats:
                _format = self.formats[format_name]
                content_type, body = _format(request, data)
                return Response(content_type=content_type, body=body)

        # render the template
        template = conf.get('/template')
        local_index = False
        if template is None:
            if 'index.html' in [ f['name'] for f in files ]:
                local_index = os.path.join(directory, 'index.html')
                template = local_index
            else:
                template = self.template
        else:
            if not os.path.isabs(template):
                _template = os.path.join(directory, template)
                if os.path.exists(_template):
                    template = _template
                else:
                    for _directory in self.template_directories:
                        if template in os.listdir(_directory):
                            break
                    else:
                        raise IOError("template %s not found" % template)
        try:
            template = self.loader.load(template)
            res = template.generate(**data).render('html', doctype='html')
        except (TemplateError, TemplateSyntaxError), e:
            if local_index:
                print repr(e)
                return self.fileserver(local_index)
            raise

        # return response
        return Response(content_type='text/html', body=res)


    ### internal methods

    def filedata(self, path, directory, conf=None):
        conf = conf or {}
        files = []

        # get data for files
        filenames = os.listdir(directory)
        for i in filenames:
            filepath = os.path.join(directory, i)
            filetype = 'file'
            if os.path.isdir(filepath):
                filetype = 'directory'
            try:
                modified = os.path.getmtime(filepath)
            except OSError:
                # the file (mysteriously) may not exist by this time(!)
                #  File "/home/jhammel/web/src/decoupage/decoupage/web.py", line 114, in __call__
                #    res = self.get(request)
                #  File "/home/jhammel/web/src/decoupage/decoupage/web.py", line 162, in get
                #    files = self.filedata(path, directory, conf)
                #  File "/home/jhammel/web/src/decoupage/decoupage/web.py", line 246, in filedata
                #    modified = os.path.getmtime(filepath)
                #  File "/home/jhammel/web/lib/python2.6/genericpath.py", line 54, in getmtime
                #    return os.stat(filename).st_mtime
                # OSError: [Errno 2] No such file or directory: '/home/jhammel/web/site/portfolio/ideas/.#index.ini'
                continue # wt{h,f}???

            modified = datetime.fromtimestamp(modified)
            data = {'path' : '%s/%s' % (path.rstrip('/'), i),
                    'name': i,
                    'modified': modified,
                    'type': filetype}
            if filetype == 'file':
                data['size'] =  os.path.getsize(filepath)
            files.append(data)

        # TODO: deal with other links in conf
        for i in conf:
            if i in filenames or i.startswith('/'):
                continue
            if i.startswith('http://') or i.startswith('https://'):
                files.append({'path': i,
                              'name': i,
                              'type': link})

        for f in files:
            f['description'] = conf.get(f['name'], None)

        return files

    def conf(self, path, cascade=None):
        """returns configuration dictionary appropriate to a path"""
        if cascade is None:
            cascase = self.cascade

        directory = os.path.join(self.directory, path.strip('/'))
        if path.strip('/'):
            path_tuple = tuple(path.strip('/').split('/'))
        else:
            path_tuple = ()

        # return cached configuration
        if hasattr(self, '_conf') and path_tuple in self._conf:
            return self._conf[path_tuple]

        conf = {}

        # local configuration
        ini_path = os.path.join(directory, 'index.ini')
        if os.path.exists(ini_path):
            _conf = ConfigMunger(ini_path).dict()
            if len(_conf) == 1:
                conf = _conf[_conf.keys()[0]].copy()

        # global configuration
        if not conf and self.configuration and os.path.exists(self.configuration):
            conf = ConfigMunger(self.configuration).dict().get('/%s' % path.rstrip('/'), {})

        # inherit and cascade configuration
        inherit_directory = None
        if '/inherit' in conf:
            inherit_directory = conf['/inherit']
        elif self.cascade and path_tuple:
            inherit_directory = '/%s' % '/'.join(path_tuple[:-1])
        if inherit_directory:
            parent_configuration = self.conf(inherit_directory)
            for key, value in parent_configuration.items():
                if key.startswith('/') and key not in conf:
                    conf[key] = value

        # cache configuration
        if not self.auto_reload:
            if not hasattr(self, '_conf'):
                self._conf = {}
            self._conf[path_tuple] = conf

        return conf

    def fmtrs(self, path):
        formatters = []
        for key, value in self.conf(path).items():
            if key.startswith('/'):
                key = key[1:]
                if key in self.formatters:
                    formatter = self.formatters[key](value)

