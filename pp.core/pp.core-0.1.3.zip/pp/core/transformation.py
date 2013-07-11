################################################################
# pp.core - Produce & Publish
# (C) 2013, ZOPYX Limited, www.zopyx.com
################################################################

import inspect
import time
import lxml.html

from pp.core.logger import LOG

TRANSFORMATIONS = dict()

def registerTransformation(method):
    """ Decorator to register a method as a transformation"""
    name = method.__name__
    TRANSFORMATIONS[name] = method

def availableTransformations():
    return TRANSFORMATIONS.keys()

def hasTransformations(transformations):
    available_transformations = availableTransformations()
    for t in transformations:
        if not t in available_transformations:
            return False
    return True

class Transformer(object):

    def __init__(self, transformation_names, context=None, destdir=None):
        self.transformation_names = transformation_names
        self.context = context
        self.destdir = destdir

    def __call__(self, html, input_encoding=None, output_encoding=unicode, return_body=False):

        if not isinstance(html, unicode):
            if not input_encoding:
                raise TypeError('Input data must be unicode')
            html = unicode(html, input_encoding)

        html = html.strip()
        if not html:
            return u''

        root = lxml.html.fromstring(html)
        errors = list()

        for name in self.transformation_names:
            method = TRANSFORMATIONS.get(name)
            params = dict(context=self.context,
                          request=getattr(self.context, 'REQUEST', None),
                          destdir=self.destdir,
                          )
            if method is None:
                raise ValueError('No transformation "%s" registered' % name)

            ts = time.time()
            argspec = inspect.getargspec(method)
            if isinstance(argspec, tuple):
                args = argspec[0] # Python 2.4
            else:
                args = argspec.args

            parameters = [root]
            if 'params' in args:
                parameters.append(params)
            if 'errors' in args:
                parameters.append(errors)

            method(*parameters)
            LOG.info('Transformation %-30s: %3.6f seconds' % (name, time.time()-ts))

        if errors:
            LOG.error('SOME ERRORS OCCURED')
        for error in errors:
            LOG.error(error)

        if return_body:
            body = root.xpath('//body')[0]
            html_new = body.text + u''.join([lxml.html.tostring(b, encoding=output_encoding) for b in body])

        else:
            html_new = lxml.html.tostring(root, encoding=output_encoding)
            if html_new.startswith('<div>') and html_new.endswith('</div>'):
                html_new = html_new[5:-6].strip()

        return html_new.strip()

def xpath_query(node_names):
    if not isinstance(node_names, (list, tuple)):
        raise TypeError('"node_names" must be a list or tuple (not %s)' % type(node_names))
    return './/*[%s]' % ' or '.join(['name()="%s"' % name for name in node_names])

