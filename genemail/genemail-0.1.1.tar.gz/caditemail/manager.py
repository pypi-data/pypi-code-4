# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# auth: Philip J Grabner <grabner@cadit.com>
# date: 2012/11/20
# copy: (C) Copyright 2012 Cadit Inc., All Rights Reserved.
#------------------------------------------------------------------------------

import os.path, yaml, email, pkg_resources, mako
from .emailprov import Email
from .sender import SmtpSender

import logging
log = logging.getLogger(__name__)

#------------------------------------------------------------------------------
__all__     = ['Manager', 'Provider', 'StringProvider', 'FileProvider', 'PkgProvider']

#------------------------------------------------------------------------------
class NoSuchResource(Exception): pass

#------------------------------------------------------------------------------
class Provider(object):
  '''
  Abstract class that defines the interface for a template/object
  provider to the :class:`caditapp.email.Manager` object. This class
  provides two types of resources: templates (via :meth:`getTemplate`,
  which must conform to the mako template API) and maps (via
  :meth:`getMap`, which must conform to the dict API).

  The following named templates can be defined (only the first of
  which is required)::

    None            # base template
    "text"          # text-only template (default: base template)
    "html"          # html-only template (default: base template)
    "subject"       # subject template (default: dynamic value from base template)

  Unless :meth:`getTemplate` is overriden, these are simply requested
  from :meth:`get` with ``.mako`` suffixed to the name and parsed as
  mako templates.

  The following named maps can be defined (none of which are required)::

    "headers"       # static map of headers (default: dynamic values from base template)
    "attachments"   # static table of attachments (default: dynamic values from base template)

  Unless :meth:`getMap` is overriden, these are simply requested from
  :meth:`get` with ``.yaml`` suffixed to the name and parsed as YAML
  documents.
  '''
  def __init__(self, lookup=None, **kw):
    super(Provider, self).__init__(**kw)
    self.lookup = lookup
  def get(self, name=None, default=None):
    '''
    Return the content for the specified `name` named resource. If not
    found or not available, `default` should be returned.
    '''
    raise NotImplementedError()
  def __getitem__(self, name):
    ret = self.get(name)
    if ret is not None:
      return ret
    raise NoSuchResource(name)
  def getTemplate(self, name=None, default=None):
    '''
    Return the mako template named `name` from the current provider.
    '''
    dat = self.get(name is not None and name + '.mako' or None, None)
    if dat is None:
      return default
    return self._makeTemplate(dat)
  def _makeTemplate(self, data):
    '''
    Generates a mako template from the specified `data`.
    '''
    return mako.template.Template(data, lookup=self.lookup, default_filters=['h'])
  def getMap(self, name, default=None):
    '''
    Return the mapping object (i.e. dict) named `name` from the
    current provider.
    '''
    dat = self.get(name + '.yaml', None)
    if dat is None:
      return default
    return yaml.load(dat)
  def getSubProvider(self, name):
    '''
    Return a provider for resource named `name` that is subsidiary to
    the current provider. The default implementation simply returns a
    :class:`caditapp.email.PrefixProvider` instance relative to the
    current provider.
    '''
    if name is None:
      return self
    return PrefixProvider(name, self)

#------------------------------------------------------------------------------
class PrefixProvider(Provider):
  '''
  A :class:`caditapp.email.Provider` implementation that simply
  prefixes any requested template or map with `name` (provided in the
  constructor) and a period (".") from the `provider` provided in the
  constructor.
  '''
  def __init__(self, name, provider, **kw):
    super(PrefixProvider, self).__init__(**kw)
    self.name     = name
    self.provider = provider
  def get(self, name=None, default=None):
    if name is None:
      return self.provider.get(self.name + '.mako', default)
    return self.provider.get(self.name + '.' + name, default)
  def getTemplate(self, name=None, default=None):
    if name is None:
      return self.provider.getTemplate(self.name, default)
    return self.provider.getTemplate(self.name + '.' + name, default)
  def getMap(self, name, default=None):
    return self.provider.getMap(self.name + '.' + name, default)

#------------------------------------------------------------------------------
class StringProvider(Provider):
  '''
  A simple :class:`caditapp.email.Provider` implementation that simply
  returns the *content* as the base template. All other resource
  requests will be responded to with the default value, or None if not
  specified.
  '''
  def __init__(self, content, **kw):
    super(StringProvider, self).__init__(**kw)
    self.content = content
  def get(self, name=None, default=None):
    if name is None: return self.content
    return default

#------------------------------------------------------------------------------
class FileProvider(Provider):
  '''
  Loads templates and maps from the filesystem. With `basedir` set to
  ``\'/path/to/base\'`` and loading email named ``welcome``, the
  following files will be loaded (where all except ``welcome.mako``
  are optional)::

    -- /path/to/base/
       |-- welcome.mako                 # base template
       |-- welcome.text.mako            # optional template for text content
       |-- welcome.html.mako            # optional template for html content
       |-- welcome.subject.mako         # optional template for subject
       |-- welcome.headers.yaml         # optional map for headers
       `-- welcome.attachments.yaml     # optional map for attachments

  See :class:`caditapp.email.Provider` for more details on templates
  and maps that can be requested and how they get resolved by default.

  The `defname` provided in the constructor is only used if an email
  is requested without a name, in which case `defname` is substituted
  for the name.

  NOTE: an issue with the current implementation is that XInclude\'s
  may not be resolved correctly. See the
  :class:`caditapp.email.MakoFileProvider` for a subclass that may
  better address your needs.
  '''
  def __init__(self, basedir, defname=None, **kw):
    super(FileProvider, self).__init__(**kw)
    self.basedir = basedir
    self.defname = defname
  def get(self, name=None, default=None):
    if name is None:
      # in theory, this should never happen...
      return self.get(os.path.join(self.basedir, self.defname + '.mako'), default)
    return self.readFile(os.path.join(self.basedir, name), default)
  def readFile(self, filename, default=None):
    try: fd = open(filename, 'rb')
    except: return default
    try: ret = fd.read()
    except: ret = default
    else: fd.close()
    return ret
  def getSubProvider(self, name):
    return super(FileProvider, self).getSubProvider(name or self.defname)

#------------------------------------------------------------------------------
class PkgProvider(FileProvider):
  '''
  Identical to :class:`caditapp.email.FileProvider` except it uses
  ``pkg_resources`` to load resources.
  '''
  def __init__(self, spec, defname=None, **kw):
    self.pkgname, root = spec.split(':', 1)
    return super(PkgProvider, self).__init__(root, defname, **kw)
  def readFile(self, filename, default=None):
    if not pkg_resources.resource_exists(self.pkgname, filename):
      return default
    try:
      ret = pkg_resources.resource_stream(self.pkgname, filename).read()
    except Exception:
      log.exception('could not load resource "%s:%s"', self.pkgname, filename)
      return default
    return ret
  def getSubProvider(self, name):
    return super(PkgProvider, self).getSubProvider(name or self.defname)

#------------------------------------------------------------------------------
class Manager(object):
  '''
  A ``caditapp.email.Manager`` object is the main clearinghouse for
  generating templatized emails. The main objective is that it
  provides access to :class:`caditapp.email.Email` objects. It
  requires access to a :class:`caditapp.email.Provider` object that
  provides templates, and objects referenced by the templates (such as
  embedded images).

  Constructor parameters:

  :param provider:
    the default :class:`caditapp.email.Provider` object (which
    provides the raw templates for the emails) for this Manager. if no
    Provider is provided, then the ``newEmail`` method will not be
    useful.

  :param sender:
    the :class:`caditapp.email.Sender` implementation that will
    actually initiate the transfer of an email to a delivery
    destination. if not provided, a default
    :class:`caditapp.email.SmtpSender` will be instantiated.
  '''

  # TODO: since the manager has to be created in order to create an
  #       Email object, i can cache templates... i should take
  #       advantage of that!...

  #----------------------------------------------------------------------------
  def __init__(self, provider=None, sender=None):
    self.provider = provider
    self.sender   = sender or SmtpSender()
    self.context  = 'caditapp.email'
    self.defaultBoundary           = None
    self.defaultTextRenderEncoding = None
    self.defaultHtmlRenderEncoding = None
    self.defaultTextEncoding       = None
    self.defaultHtmlEncoding       = None
    self.defaultTransferEncoding   = None
    self.defaultEncoding           = None
    self.defaultMaxSubjectLength   = None
    self.defaultSnipIndicator      = '[...]'

  #----------------------------------------------------------------------------
  def newEmail(self, name=None):
    '''
    Creates and returns a new :class:`caditapp.email.Email` object
    that will be based on the templates named `name` from the current
    :class:`caditapp.email.Provider` object. Note that for most
    providers, a ``None`` `name` is valid and refers to the default
    template.
    '''
    return Email(manager=self, provider=self.provider.getSubProvider(name))

  #----------------------------------------------------------------------------
  def newEmailFromTemplate(self, template):
    '''
    Creates and returns a new :class:`caditapp.email.Email` object
    that will be based on the provided string `template`. A
    :class:`caditapp.email.StringProvider` will be created to provide
    the template to the :class:`caditapp.email.Email` object.
    Although the returned object will not use the manager\'s Provider,
    it *will* use the manager\'s sender.
    '''
    return Email(manager=self, provider=StringProvider(template))

  #----------------------------------------------------------------------------
  def updateHeaders(self, emailobj, headers):
    defaultHeaders = {
      'Date':        lambda: email.Utils.formatdate(),
      'Message-ID':  lambda: email.Utils.make_msgid(self.context),
      }
    for name, call in defaultHeaders.items():
      if headers.has_key(name):
        continue
      headers[name] = call()

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
