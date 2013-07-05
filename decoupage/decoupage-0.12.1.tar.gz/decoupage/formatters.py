#!/usr/bin/env python

import random
import sys
from datetime import datetime
from fnmatch import fnmatch
from pkg_resources import iter_entry_points

### abstract base classes for formatters

class FormatterBase(object):
    """
    abstract base class if you want to use __init__ methods
    in the form of
    'arg1, arg2, arg3, kw1=foo, kw2=bar, kw3=baz
    """

    defaults = {} # default values for attrs to be set on the instance

    def __init__(self, string):
        self._string = string
        args = [ i.strip() for i in string.split(',')]
        for index, arg in enumerate(args):
            if '=' in arg:
                break
        else:
            self.args = args
            for key, default in self.defaults.items():
                setattr(self, key, default)
            return
        self.args = args[:index]
        self.kw = dict([i.split('=', 1) for i in args[index:]])
        for key, default in self.defaults.items():
            value = self.kw.pop(key, default)
            setattr(self, key, value)


### formatters

class Ignore(object):
    """
    ignore files of a glob patterns.
    These files will not be linked to in the template.
    e.g. /ignore = .* *.pdf  # don't list dotfiles and PDFs
    """

    def __init__(self, ignore):
        self.match = ignore.split()

    def __call__(self, request, data):
        _files = []
        for f in data['files']:
            for pattern in self.match:
                if fnmatch(f['name'], pattern):
                    break
            else:
                _files.append(f)
        data['files'] = _files


class All(object):
    """
    only pass files of a certain pattern;
    the inverse of ignore
    calling all with no arguments means only files with descriptions are used
    """

    def __init__(self, pattern):
        self.match = pattern.split()

    def __call__(self, request, data):
        _files = []
        for f in data['files']:
            if self.match:
                for pattern in self.match:
                    if fnmatch(f['name'], pattern):
                        _files.append(f)
                        break
            else:
                # use only files where the title or description is not None
                if (f['description'] is not None) or (f.get('title') is not None):
                    _files.append(f)
        data['files'] = _files


class Sort(FormatterBase):
    """
    determines how to sort the files in a directory;
    right now only by case-insensitive alphabetically
    * reverse : reverse the order of the sorting
    """
    defaults = {'order': 'name'}

    def __init__(self, pattern):
        FormatterBase.__init__(self, pattern)
        self.orders = {'name': self.name,
                       'random': self.random,
                       }
        # TODO: date

    def __call__(self, request, data):

        sort = self.orders.get(request.GET.get('order', self.order), self.name)
        data['files'] = sort(data['files'])

        if 'reverse' in self.args:
            data['files'] = list(reversed(data['files']))

    def name(self, files):
        return sorted(files, key=lambda x: x['name'].lower())

    def random(self, files):
        random.shuffle(files)
        return files


class Order(object):
    """
    put the files in a particular order
    """
    def __init__(self, pattern):
        if '=' in pattern:
            key, value = pattern.split('=', 1)
            assert key == 'file'
            self.file = value
        else:
            self.order = [i.strip() for i in pattern.split(',')]

    def __call__(self, request, data):

        if self.file:
            raise NotImplementedError

        files = []
        file_hash = dict([(i['name'], i) for i in data['files']])
        for f in self.order:
            files.append(file_hash.get(f, None))
        files = [ i for i in files if i is not None ]


class FilenameDescription(FormatterBase):
    """
    obtain the description from the filename
    the file extension (if any) will be dropped and
    spaces will be substituted for underscores
    """
    # TODO : deal with CamelCaseFilenames

    separators = ['_', '-'] # space substitute separators
    lesser_words = [ 'or', 'a', 'the', 'on', 'of' ] # unimportant words

    def __call__(self, request, data):
        for f in data['files']:
            if f['description'] is None:
                description = f['name']
                if '.' in description:
                    description = description.rsplit('.', 1)[0]
                decription = description.strip('_')
                for separator in self.separators:
                    if separator in description:
                        description = ' '.join([(i in self.lesser_words) and i or i.title()
                                                for i in description.split(separator)])
                        description = description[0].upper() + description[1:]
                f['description'] = description


class TitleDescription(FormatterBase):
    """
    splits a description into a title and a description via a separator in
    the description.  The template will now have an additional variable,
    'title', per file
    Arguments:
    * separator: what separator to use (':' by default)
    """
    # XXX what about setting the page title?

    defaults = { 'separator': ':' }

    def __call__(self, request, data):

        # title webpage
        title = self._string
        if ':' in title:
            _title, url = [i.strip() for i in title.split(':', 1)]
            if '://' in url:
                # XXX could also use urlparse
                title = _title
                data['link'] = url
        data['title'] = title

        # title files
        for f in data['files']:
            if f['description'] and self.separator in f['description']:
                title, description = f['description'].split(self.separator, 1)
                title = title.strip()
                description = description.strip()
                if not title:
                    title = f['name']
                f['title'] = title
                f['description'] = description
            else:
                f['title'] = f['description']
                f['description'] = None

class Datestamp(FormatterBase):
    """
    datestamps for modified times
    """
    # TODO:
    # - currently we only do modified; TODO: created/modified/etc
    # - use modified dateutil from bitsyblog;
    # - e.g. javascript for things like e.g. "Yesterday"
    key = 'modified'

    def __init__(self, string):
        FormatterBase.__init__(self, string)

        # check formatting string now v later
        datetime.now().strftime(self._string)

    def __call__(self, request, data):
        for f in data['files']:
            _datetime = f.get(self.key)
            if not _datetime:
                continue
            try:
                datestamp = _datetime.strftime(self._string)
                f['datestamp'] = datestamp
            except:
                raise # TODO: handle more better

class Links(FormatterBase):
    """
    allow list of links per item:
    foo.html = description of foo; [PDF]=foo.pdf; [TXT]=foo.txt
    """

    fatal = False
    defaults = {'separator': ';'}


    def __call__(self, request, data):
        for f in data['files']:
            if f['description'] and self.separator in f['description']:
                description, links = f['description'].split(self.separator, 1)
                links = links.rstrip().split(self.separator)

                if not min(['=' in link for link in links]):
                    message = """%s

%s: misformatted description: %s (separator: %s)""" % (f,
                                                       self.__class__.__name__,
                                                       description,
                                                       self.separator)
                    if self.fatal:
                        raise AssertionError(message)
                    else:
                        print >> sys.stderr, message
                        continue

                f['description'] = description

                links = [link.split('=', 1) for link in links]
                f['links'] = [{'text': text, 'link': link}
                              for text, link in links]


class Up(object):
    """
    provides an up link to the path above:
    /up = ..
    """

    def __init__(self, arg):
        self.up = arg.strip()

    def __call__(self, request, data):
        path = request.path_info
        if (path != '/') and self.up:
            data['files'].insert(0, {'path': '..',
                                     'type': 'directory',
                                     'name': path.rsplit('/', 1)[0] + '/',
                                     'description': self.up})

class CSS(object):
    """specify CSS used (whitespace separated list)"""

    def __init__(self, arg):
        self.css = arg.split()
    def __call__(self, request, data):
        data['css'] = self.css

class JavaScript(object):
    """specify JS for the page"""

    def __init__(self, arg):
        self.scripts = arg.split()
    def __call__(self, request, data):
        data['scripts'] = self.scripts

class Favicon(object):
    """specify favicons for the page"""

    def __init__(self, icon):
        self.icon = icon
    def __call__(self, request, data):
        data['icon'] = self.icon

class Include(object):
    """include a file at the top of the body"""

    def __init__(self, arg):
        self.include = arg
    def __call__(self, request, data):
        data['include'] = self.include

###

def formatters():
    formatters = {}
    for entry_point in iter_entry_points('decoupage.formatters'):
        try:
            formatter = entry_point.load()
        except:
            continue
        formatters[entry_point.name] = formatter
    return formatters

def main(args=sys.argv[1:]):
    for name, formatter in formatters().items():
        print '%s%s' % (name, formatter.__doc__ and ': ' + formatter.__doc__ or '')

if __name__ == '__main__':
    main()
