# -*- coding: utf-8 -*-
#------------------------------------------------------------------------------
# file: $Id$
# auth: Philip J Grabner <grabner@cadit.com>
# date: 2012/11/20
# copy: (C) Copyright 2012 Cadit Inc., All Rights Reserved.
#------------------------------------------------------------------------------

'''
An email template abstraction class -- see :class:`caditapp.email.manager`
for details.
'''

#------------------------------------------------------------------------------
# IMPORTS
#------------------------------------------------------------------------------

import re, mimetypes, cssutils, base64, codecs, mako, cssselect
from StringIO import StringIO
import xml.etree.ElementTree as ET
import xpath
from xml.dom import minidom
import email.Encoders, email.Message, email.MIMEMultipart, email.MIMEText
import email.MIMEImage, email.Utils
import html2text

from .idict import idict
from .sender import SmtpSender

#------------------------------------------------------------------------------
# GLOBALS
#------------------------------------------------------------------------------

xmlns = 'http://xmlns.cadit.com/caditapp/email/1.0'
htmlns = 'http://www.w3.org/1999/xhtml'
class MissingHeader(Exception): pass

#------------------------------------------------------------------------------
# TODO: put extractEmails(), getHtmlStyleView() and inlineHtml() in a better place
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------
# TODO: move this...
#------------------------------------------------------------------------------
# email regex from:
#   http://www.regular-expressions.info/email.html
# and extended to support "...@localhost"
def extractEmails(s):
  if not s:
    return None
  emailRegex = '\\b[A-Z0-9._%+-]+@(?:(?:[A-Z0-9-]+\\.)+[A-Z]{2,4}|localhost)\\b'
  return re.findall(emailRegex, s, re.I)

#------------------------------------------------------------------------------
# TODO: move this...
def getHtmlStyleView(document, css, media='all', name=None,
                     styleCallback=lambda element: None):
  """
  :param document:
    a DOM element (must be minidom-compatible)
  :param css:
    a CSS StyleSheet string
  :param media:
    [optional] TODO: view for which media it should be
  :param name:
    [optional] TODO: names of sheets only
  :param styleCallback:
    [optional] should return css.CSSStyleDeclaration of inline styles,
    for html a style declaration for ``element@style``. Gets one
    parameter ``element`` which is the relevant DOMElement

  returns style view
    a dict of {DOMElement: css.CSSStyleDeclaration} for html

  shamelessly scrubbed from:
    http://cssutils.googlecode.com/svn/trunk/examples/style.py (``getView()``)
    ==> with an adjustment to get around a deprecationwarning in
        cssutils/css/cssstyledeclaration.py:598
    ==> and an adjustment to use "xhtml" translator for the cssselector
  """

  sheet = cssutils.parseString(css)
  css2xpath = cssselect.GenericTranslator()
  view = {}
  specificities = {} # needed temporarily
  # TODO: filter rules simpler?, add @media
  rules = (rule for rule in sheet if rule.type == rule.STYLE_RULE)
  for rule in rules:
    for selector in rule.selectorList:
      xpe = css2xpath.css_to_xpath(selector.selectorText)
      for element in xpath.find(xpe, document):
        if element not in view:
          # add initial empty style declatation
          view[element] = cssutils.css.CSSStyleDeclaration()
          specificities[element] = {}
          # and add inline @style if present
          inlinestyle = styleCallback(element)
          if inlinestyle:
            for p in inlinestyle:
              # set inline style specificity
              view[element].setProperty(p)
              specificities[element][p.name] = (1,0,0,0)
        for p in rule.style:
          # update style declaration
          if p not in view[element]:
            # setProperty needs a new Property object and
            # MUST NOT reuse the existing Property
            # which would be the same for all elements!
            # see Issue #23
            view[element].setProperty(p.name, p.value, p.priority)
            specificities[element][p.name] = selector.specificity
          else:
            sameprio = (p.priority ==
                  view[element].getPropertyPriority(p.name))
            if not sameprio and bool(p.priority) or (
               sameprio and selector.specificity >=
                    specificities[element][p.name]):
              # later, more specific or higher prio
              # NOTE: added explicit removeProperty to get around these warnings:
              #   cssutils-0.9.8a1-py2.6.egg/cssutils/css/cssstyledeclaration.py:598: DeprecationWarning: Call to deprecated method '_getCSSValue'. Use ``property.propertyValue`` instead.
              #   cssutils-0.9.8a1-py2.6.egg/cssutils/css/cssstyledeclaration.py:598: DeprecationWarning: Call to deprecated method '_setCSSValue'. Use ``property.propertyValue`` instead.
              view[element].removeProperty(p.name)
              view[element].setProperty(p.name, p.value, p.priority)
  return view

#------------------------------------------------------------------------------
# TODO: move this to use ET elements to remove the XML roundtrip...
# TODO: this currently strips out the <!DOCTYPE> line if it appears, eg:
#       <!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
def inlineHtmlStyling_minidom(doc, css):
  def scb(element):
    if element.hasAttribute('style'):
      cssText = element.getAttribute('style')
      return cssutils.css.CSSStyleDeclaration(cssText=cssText)
    return None
  view = getHtmlStyleView(doc, css, styleCallback=scb)
  for element, style in view.items():
    v = style.getCssText(separator=u'')
    element.setAttribute('style', v)
  return doc
def inlineHtmlStyling(etdoc, css):
  html = serializeHtml(etdoc)
  doc  = minidom.parseString(html)
  ret  = inlineHtmlStyling_minidom(doc, css)
  return parseXml(ret.toxml('UTF-8'))

#------------------------------------------------------------------------------
def parseXml(data):
  src = StringIO(data)
  parser = ET.XMLParser()
  parser.parser.UseForeignDTD(True)
    # todo: allow some mechanism for the caller to provide additional entities
  parser.entity['nbsp']  = unichr(160)
  parser.entity['mdash'] = unichr(8212)
  parser.entity['copy']  = unichr(169)
  parser.entity['reg']   = unichr(174)
  etree = ET.ElementTree()
  tree = etree.parse(src, parser=parser)
  return tree

#------------------------------------------------------------------------------
def serializeHtml(xdoc):
  '''
  Serializes ElementTree `xdoc` to HTML.
  NOTE: `xdoc` is mutated to qualify any non-qualified attributes
  and elements with the HTML namespace.
  '''
  # note: qualifying all attributes and elements so that this error is
  # avoided:
  #   ValueError: cannot use non-qualified names with default_namespace option
  # IMHO, it should not be throwing this...
  # http://bugs.python.org/issue17088
  for node in xdoc.iter():
    if not node.tag.startswith('{'):
      node.tag = '{%s}%s' % (htmlns, node.tag)
    for attr in list(node.keys()):
      if not attr.startswith('{'):
        node.set('{%s}%s' % (htmlns, attr), node.get(attr))
        del node.attrib[attr]
  dst = StringIO()
  etree = ET.ElementTree(xdoc)
  etree.write(dst, default_namespace=htmlns)
  # todo: it would be nice if the HTML output were 'pretty-printed'...
  return dst.getvalue()

#------------------------------------------------------------------------------
# shamelessly scrubbed from:
#   http://www.w3schools.com/tags/ref_symbols.asp
# with additions for &copy; and &reg;
r2a_map = dict((

  (u'\u00a9', '(C)'),                  # © &#169; &copy; copyright symbol
  (u'\u00ae', '(R)'),                  # ® &#174; &reg; registered trademark

  # math symbols supported by HTML
  (u'\u2200', '<for-all>'),            # ∀ &#8704; &forall; for all
  (u'\u2202', '<part>'),               # ∂ &#8706; &part; part
  (u'\u2203', '<exists>'),             # ∃ &#8707; &exist; exists
  (u'\u2205', '<empty>'),              # ∅ &#8709; &empty; empty
  (u'\u2207', '<nabla>'),              # ∇ &#8711; &nabla; nabla
  (u'\u2208', '<isin>'),               # ∈ &#8712; &isin; isin
  (u'\u2209', '<notin>'),              # ∉ &#8713; &notin; notin
  (u'\u220b', '<ni>'),                 # ∋ &#8715; &ni; ni
  (u'\u220f', '<prod>'),               # ∏ &#8719; &prod; prod
  (u'\u2211', '<sum>'),                # ∑ &#8721; &sum; sum
  (u'\u2212', '<minus>'),              # − &#8722; &minus; minus
  (u'\u2217', '<lowast>'),             # ∗ &#8727; &lowast; lowast
  (u'\u221a', '<square-root>'),        # √ &#8730; &radic; square root
  (u'\u221d', '<proportional-to>'),    # ∝ &#8733; &prop; proportional to
  (u'\u221e', '<infinity>'),           # ∞ &#8734; &infin; infinity
  (u'\u2220', '<angle>'),              # ∠ &#8736; &ang; angle
  (u'\u2227', '<and>'),                # ∧ &#8743; &and; and
  (u'\u2228', '<or>'),                 # ∨ &#8744; &or; or
  (u'\u2229', '<cap>'),                # ∩ &#8745; &cap; cap
  (u'\u222a', '<cup>'),                # ∪ &#8746; &cup; cup
  (u'\u222b', '<integral>'),           # ∫ &#8747; &int; integral
  (u'\u2234', '<therefore>'),          # ∴ &#8756; &there4; therefore
  (u'\u223c', '<similar-to>'),         # ∼ &#8764; &sim; similar to
  (u'\u2245', '<congruent-to>'),       # ≅ &#8773; &cong; congruent to
  (u'\u2248', '<almost-equal>'),       # ≈ &#8776; &asymp; almost equal
  (u'\u2260', '<not-equal>'),          # ≠ &#8800; &ne; not equal
  (u'\u2261', '<equivalent>'),         # ≡ &#8801; &equiv; equivalent
  (u'\u2264', '<less-or-equal>'),      # ≤ &#8804; &le; less or equal
  (u'\u2265', '<greater-or-equal>'),   # ≥ &#8805; &ge; greater or equal
  (u'\u2282', '<subset-of>'),          # ⊂ &#8834; &sub; subset of
  (u'\u2283', '<superset-of>'),        # ⊃ &#8835; &sup; superset of
  (u'\u2284', '<not-subset-of>'),      # ⊄ &#8836; &nsub; not subset of
  (u'\u2286', '<subset-or-equal>'),    # ⊆ &#8838; &sube; subset or equal
  (u'\u2287', '<superset-or-equal>'),  # ⊇ &#8839; &supe; superset or equal
  (u'\u2295', '<circled-plus>'),       # ⊕ &#8853; &oplus; circled plus
  (u'\u2297', '<circled-times>'),      # ⊗ &#8855; &otimes; circled times
  (u'\u22a5', '<perpendicular>'),      # ⊥ &#8869; &perp; perpendicular
  (u'\u22c5', '<dot-operator>'),       # ⋅ &#8901; &sdot; dot operator

  # greek letters supported by HTML
  (u'\u0391', '<Alpha>'),              # Α &#913; &Alpha; Alpha
  (u'\u0392', '<Beta>'),               # Β &#914; &Beta; Beta
  (u'\u0393', '<Gamma>'),              # Γ &#915; &Gamma; Gamma
  (u'\u0394', '<Delta>'),              # Δ &#916; &Delta; Delta
  (u'\u0395', '<Epsilon>'),            # Ε &#917; &Epsilon; Epsilon
  (u'\u0396', '<Zeta>'),               # Ζ &#918; &Zeta; Zeta
  (u'\u0397', '<Eta>'),                # Η &#919; &Eta; Eta
  (u'\u0398', '<Theta>'),              # Θ &#920; &Theta; Theta
  (u'\u0399', '<Iota>'),               # Ι &#921; &Iota; Iota
  (u'\u039a', '<Kappa>'),              # Κ &#922; &Kappa; Kappa
  (u'\u039b', '<Lambda>'),             # Λ &#923; &Lambda; Lambda
  (u'\u039c', '<Mu>'),                 # Μ &#924; &Mu; Mu
  (u'\u039d', '<Nu>'),                 # Ν &#925; &Nu; Nu
  (u'\u039e', '<Xi>'),                 # Ξ &#926; &Xi; Xi
  (u'\u039f', '<Omicron>'),            # Ο &#927; &Omicron; Omicron
  (u'\u03a0', '<Pi>'),                 # Π &#928; &Pi; Pi
  (u'\u03a1', '<Rho>'),                # Ρ &#929; &Rho; Rho
  (u'\u03a3', '<Sigma>'),              # Σ &#931; &Sigma; Sigma
  (u'\u03a4', '<Tau>'),                # Τ &#932; &Tau; Tau
  (u'\u03a5', '<Upsilon>'),            # Υ &#933; &Upsilon; Upsilon
  (u'\u03a6', '<Phi>'),                # Φ &#934; &Phi; Phi
  (u'\u03a7', '<Chi>'),                # Χ &#935; &Chi; Chi
  (u'\u03a8', '<Psi>'),                # Ψ &#936; &Psi; Psi
  (u'\u03a9', '<Omega>'),              # Ω &#937; &Omega; Omega
  (u'\u03b1', '<alpha>'),              # α &#945; &alpha; alpha
  (u'\u03b2', '<beta>'),               # β &#946; &beta; beta
  (u'\u03b3', '<gamma>'),              # γ &#947; &gamma; gamma
  (u'\u03b4', '<delta>'),              # δ &#948; &delta; delta
  (u'\u03b5', '<epsilon>'),            # ε &#949; &epsilon; epsilon
  (u'\u03b6', '<zeta>'),               # ζ &#950; &zeta; zeta
  (u'\u03b7', '<eta>'),                # η &#951; &eta; eta
  (u'\u03b8', '<theta>'),              # θ &#952; &theta; theta
  (u'\u03b9', '<iota>'),               # ι &#953; &iota; iota
  (u'\u03ba', '<kappa>'),              # κ &#954; &kappa; kappa
  (u'\u03bb', '<lambda>'),             # λ &#955; &lambda; lambda
  (u'\u03bc', '<mu>'),                 # μ &#956; &mu; mu
  (u'\u03bd', '<nu>'),                 # ν &#957; &nu; nu
  (u'\u03be', '<xi>'),                 # ξ &#958; &xi; xi
  (u'\u03bf', '<omicron>'),            # ο &#959; &omicron; omicron
  (u'\u03c0', '<pi>'),                 # π &#960; &pi; pi
  (u'\u03c1', '<rho>'),                # ρ &#961; &rho; rho
  (u'\u03c2', '<sigmaf>'),             # ς &#962; &sigmaf; sigmaf
  (u'\u03c3', '<sigma>'),              # σ &#963; &sigma; sigma
  (u'\u03c4', '<tau>'),                # τ &#964; &tau; tau
  (u'\u03c5', '<upsilon>'),            # υ &#965; &upsilon; upsilon
  (u'\u03c6', '<phi>'),                # φ &#966; &phi; phi
  (u'\u03c7', '<chi>'),                # χ &#967; &chi; chi
  (u'\u03c8', '<psi>'),                # ψ &#968; &psi; psi
  (u'\u03c9', '<omega>'),              # ω &#969; &omega; omega
  (u'\u03d1', '<theta-symbol>'),       # ϑ &#977; &thetasym; theta symbol
  (u'\u03d2', '<upsilon-symbol>'),     # ϒ &#978; &upsih; upsilon symbol
  (u'\u03d6', '<pi-symbol>'),          # ϖ &#982; &piv; pi symbol

  # other symbols supported by HTML
  (u'\u0152', 'OE'),                   # Œ &#338; &OElig; capital ligature OE
  (u'\u0153', 'oe'),                   # œ &#339; &oelig; small ligature oe
  # TODO: should these be decorated?...
  (u'\u0160', 'S'),                    # Š &#352; &Scaron; capital S with caron
  (u'\u0161', 's'),                    # š &#353; &scaron; small S with caron
  (u'\u0178', 'Y'),                    # Ÿ &#376; &Yuml; capital Y with diaeres
  (u'\u0192', '?'),                    # ƒ &#402; &fnof; f with hook

  (u'\u02c6', '^'),                    # ˆ &#710; &circ; modifier letter circumflex accent
  (u'\u02dc', '~'),                    # ˜ &#732; &tilde; small tilde
  (u'\u2002', ' '),                    #   &#8194; &ensp; en space
  (u'\u2003', ' '),                    #   &#8195; &emsp; em space
  (u'\u2009', ' '),                    #   &#8201; &thinsp; thin space
  (u'\u200c', '?'),                    # ‌ &#8204; &zwnj; zero width non-joiner
  (u'\u200d', '?'),                    # ‍ &#8205; &zwj; zero width joiner
  (u'\u200e', '?'),                    # ‎ &#8206; &lrm; left-to-right mark
  (u'\u200f', '?'),                    # ‏ &#8207; &rlm; right-to-left mark
  (u'\u2013', '-'),                    # – &#8211; &ndash; en dash
  (u'\u2014', '-'),                    # — &#8212; &mdash; em dash
  (u'\u2018', '\''),                   # ‘ &#8216; &lsquo; left single quotation mark
  (u'\u2019', '\''),                   # ’ &#8217; &rsquo; right single quotation mark
  (u'\u201a', '\''),                   # ‚ &#8218; &sbquo; single low-9 quotation mark
  (u'\u201c', '"'),                    # “ &#8220; &ldquo; left double quotation mark
  (u'\u201d', '"'),                    # ” &#8221; &rdquo; right double quotation mark
  (u'\u201e', '"'),                    # „ &#8222; &bdquo; double low-9 quotation mark
  (u'\u2020', '?'),                    # † &#8224; &dagger; dagger
  (u'\u2021', '?'),                    # ‡ &#8225; &Dagger; double dagger
  (u'\u2022', '*'),                    # • &#8226; &bull; bullet
  (u'\u2026', '...'),                  # … &#8230; &hellip; horizontal ellipsis
  (u'\u2030', '0/00'),                 # ‰ &#8240; &permil; per mille
  (u'\u2032', '\''),                   # ′ &#8242; &prime; minutes
  (u'\u2033', '"'),                    # ″ &#8243; &Prime; seconds
  (u'\u2039', '<'),                    # ‹ &#8249; &lsaquo; single left angle quotation
  (u'\u203a', '>'),                    # › &#8250; &rsaquo; single right angle quotation
  (u'\u203e', '-'),                    # ‾ &#8254; &oline; overline
  (u'\u20ac', '<euro>'),               # € &#8364; &euro; euro
  (u'\u2122', '<TM>'),                 # ™ &#8482; &trade; trademark
  (u'\u2190', '<-'),                   # ← &#8592; &larr; left arrow
  (u'\u2191', '?'),                    # ↑ &#8593; &uarr; up arrow
  (u'\u2192', '->'),                   # → &#8594; &rarr; right arrow
  (u'\u2193', '?'),                    # ↓ &#8595; &darr; down arrow

  # additional right arrows scrubbed from:
  #   http://right-arrow.net/
  (u'\u21d2', '=>'),                   # ⇒ &#8658; &rArr;
  (u'\u21ac', '->'),                   # ↬ &#8620;
  (u'\u21c9', '=>'),                   # ⇉ &#8649;
  (u'\u21e8', '=>'),                   # ⇨ &#8680;
  (u'\u21e5', '->|'),                  # ⇥ &#8677;
  (u'\u21e2', '->'),                   # ⇢ &#8674;
  (u'\u21aa', '->'),                   # ↪ &#8618;
  (u'\u21a6', '|->'),                  # ↦ &#8614;
  (u'\u21f6', '=>'),                   # ⇶ &#8694;
  (u'\u21a3', '>->'),                  # ↣ &#8611;
  (u'\u21f0', '|=>'),                  # ⇰ &#8688;
  (u'\u219d', '~>'),                   # ↝ &#8605;
  (u'\u21a0', '->>'),                  # ↠ &#8608;
  (u'\u21fe', '->'),                   # ⇾ &#8702;

  # others...
  (u'\u21e6', '<='),                   # ⇦ &#8678;

  ))

def reduce2ascii(text):
  ret = []
  for c in text:
    if ord(c) < 128:
      ret.append(c)
      continue
    # todo: handle ascii chars in the 128 -> 255 range...
    ret.append(r2a_map.get(c, '?'))
  return ''.join(ret)
  #return text.replace(u'\u21d2', '=>')

#------------------------------------------------------------------------------
_removeCidsRe = re.compile('\\!\\[([^\\]]*)\\]\\(cid:[^)]*\\)')
def removeCids(text):
  return _removeCidsRe.sub('[\\1]', text)

#------------------------------------------------------------------------------
# todo: move this?
smtp_header_element_upper = ['cc', 'id', 'spf']
def smtpHeaderFormat(h):
  return '-'.join([e.upper() if e in smtp_header_element_upper else e.title()
                   for e in [e.lower() for e in h.split('-')]])

#------------------------------------------------------------------------------
# todo: installing a global unicode decode/encode translation error handler...
#       this is not ideal... see Email.getSubject() for details...
#------------------------------------------------------------------------------
def caditapp_email_unicode2ascii(err):
  if err.reason != 'ordinal not in range(128)':
    raise err
  # todo: shouldn't this just use `r2a_map`?...
  if err.object[err.start] == unichr(160):
    # &nbsp;
    return (u' ', err.start + 1)
  if err.object[err.start] == unichr(8212):
    # &mdash;
    return (u'--', err.start + 1)
  return (u'?', err.start + 1)
#------------------------------------------------------------------------------
try:
  codecs.lookup_error('caditapp_email_unicode2ascii')
except LookupError:
  codecs.register_error('caditapp_email_unicode2ascii', caditapp_email_unicode2ascii)

extractEnv_expr = re.compile(
  '<email:env\s+name\s*=\s*"([^"]*)"\s*>(.*?)</email:env>', flags=re.DOTALL)

#------------------------------------------------------------------------------
class Email(object):
  '''
  The ``caditapp.email.Email`` object provides access to an email
  template, such that formally specified emails can be easily
  generated.

  Email headers (i.e. ``To``, ``From``, ``Received``, etc) can be set
  via the :meth:`setHeader` method. It is recommended to set at least
  the ``To`` and ``From`` headers, either via the API or from the
  template (as documented in the :mod:`caditapp.email` module).

  Variables used by the underlying mako template rendering are
  specified using Email object item attributes, for example::

    email = caditapp.email.Manager(...).newEmail(...)
    email['givenname'] = 'John'
    email['surname'] = 'Doe'
    email.setHeader('To', 'john.doe@example.com')
    email.setHeader('From', 'noreply@example.com')
    email.send()
  '''

  #----------------------------------------------------------------------------
  def __init__(self, manager, provider=None, name=None):
    self.manager            = manager
    self.provider           = provider or manager.provider
    self.name               = name
    self.style              = None
    self.include            = ['text', 'html', 'attachments']
    self.textRenderEncoding = self.manager.defaultTextRenderEncoding
    self.htmlRenderEncoding = self.manager.defaultHtmlRenderEncoding
    self.textEncoding       = self.manager.defaultTextEncoding
    self.htmlEncoding       = self.manager.defaultHtmlEncoding
    self.transferEncoding   = self.manager.defaultTransferEncoding
    self.encoding           = self.manager.defaultEncoding
    self.maxSubjectLength   = self.manager.defaultMaxSubjectLength
    self.snipIndicator      = self.manager.defaultSnipIndicator
    self.headers            = idict()
    self.params             = {}
    self.attachments        = []
    self.boundary           = self.manager.defaultBoundary
    self.template           = self.provider.getTemplate(self.name)
    self.cidRewrite         = None
    self.attachmentTable    = None
    for key, val in self.provider.getMap('headers', {}).items():
      self.headers[key] = val

  #----------------------------------------------------------------------------
  def __setitem__(self, key, val): self.params[key] = val
  def __getitem__(self, key): return self.params[key]
  def __delitem__(self, key): del self.params[key]

  #----------------------------------------------------------------------------
  def setHeader(self, key, val):
    'Set the email header `key` to `val`, overriding all other header sources.'
    self.headers[key] = val

  #----------------------------------------------------------------------------
  def getHeader(self, key):
    '''
    Get the current value of the header `key`. Note that this will only return
    the value as set with a prior :meth:`setHeader` call - it will *not*
    extract headers set by the template(s).
    '''
    return self.headers[key]

  #----------------------------------------------------------------------------
  def hasHeader(self, key):
    '''
    Returns whether or not the header `key` has been set with a prior call
    to :meth:`setHeader` - it will *not* extract headers set by the template(s).
    '''
    return self.headers.has_key(key)

  #----------------------------------------------------------------------------
  def delHeader(self, key):
    '''
    If the header `key` had been set with a prior call to
    :meth:`setHeader`, this will unset the header. Note that it will
    *not* delete any headers set by the template(s).
    '''
    del self.headers[key]

  #----------------------------------------------------------------------------
  def getEnvs(self):
    '''
    Returns a dictionary of parameters set by the template (this is so
    that templates can communicate non-output parameters back to the
    calling application).
    '''
    # TODO: this is all wrong. need to re-architect this.
    ret = dict()
    for match in extractEnv_expr.finditer(self.template.source):
      # todo: ugh. i need to do XML un-escaping too...
      ret[match.group(1)] = match.group(2)
    return ret

  #----------------------------------------------------------------------------
  def getEnv(self, key, default=None):
    '''
    Returns the template-set parameter name `key`. If not set, `default`
    is returned. See :meth:`getEnvs` for details.
    '''
    return self.getEnvs().get(key, default)

  #----------------------------------------------------------------------------
  def addAttachment(self, name, value, cid=False, contentType=None):
    '''
    Add an attachment to the email. The `name` is the default filename that
    will be offered when the recipient tries to "Save..." the attachment. The
    `value` is the actual content of the attachment. If `cid` is True, then
    the attachment will be stored as an embedded object, and will therefore
    not be directly saveable by the recipient and it can be accessed from
    within the HTML, for example, with the `name` set to ``'logo.png'``, the
    following will result in a valid image reference in the HTML::

      <img alt="The Logo" src="cid:logo.png"/>

    (note the ``cid:`` prefix.)
    '''
    att = dict(name=name, value=value, cid=cid)
    if contentType is not None:
      att['content-type'] = contentType
    self.attachments.append(att)

  #----------------------------------------------------------------------------
  def setStyle(self, css):
    '''
    Add the specified CSS style instructions to the current HTML rendering.
    Note the following current limitations of the underlying CSS engine:

      * element names must be lowercase, e.g. "p {...}", not "P {....}"
      * "body" element cannot be targeted, e.g. "body {...}" does NOT work
    '''
    self.style = css

  #----------------------------------------------------------------------------
  def getTemplateXml(self):
    # todo: use TemplateLookup?... if so, make sure to use the manager's...
    #         ie something like ``self.manager.makoLookup``...
    # todo: filesystem_checks=False configurable
    return parseXml(self.template.render(**self.params))

  #----------------------------------------------------------------------------
  def getTemplateHeaders(self):
    ret = {}
    # todo: this requires that headers be defined as separate elements, eg:
    #         <email:header name="..." value="...">...</email:header>
    #       rather than being able to tag an existing node, such as:
    #         <p>This email was sent to <span email:header="To">...</span>.</p>
    xdoc = self.getTemplateXml()
    etag = '{%s}header' % (xmlns,)
    for node in xdoc.iter():
      if node.tag == etag:
        ret[node.get('name')] = node.get('value') or node.text
        continue
      if node.get(etag) is not None:
        ret[node.get(etag)] = node.text
    return ret

  #----------------------------------------------------------------------------
  def getTemplateAttachments(self):
    ret = []
    xdoc = self.getTemplateXml()
    for node in xdoc.iter('{%s}attachment' % (xmlns,)):
      attm  = dict(name = node.get('name'),
                   cid  = node.get('cid', 'false').lower() == 'true')
      value = node.get('value', None) or node.text
      if node.get('encoding', None) == 'base64':
        value = base64.b64decode(value)
      attm['value'] = value
      ct = node.get('content-type', None)
      if ct is not None:
        attm['content-type'] = ct
      ret.append(attm)
    return ret

  #----------------------------------------------------------------------------
  def getTemplateStyle(self):
    ret  = []
    xdoc = self.getTemplateXml()
    # todo: what if the node has a "src" attribute...
    for node in xdoc.findall('{%s}head/{%s}style[@type="text/css"]' % (htmlns, htmlns)):
      ret.append(node.text)
    return ' '.join(ret)

  #----------------------------------------------------------------------------
  def getHtml(self, standalone=False):
    '''
    Returns the raw HTML that would be generated if the email were
    sent with the current settings. Use :meth:`send` to actually send
    the email.
    '''

    if standalone:
      ret = self.getHtml()
      return self.inlineCidAttachments(ret)

    tpl = self.provider.getTemplate('html', self.template)
    html = tpl.render(**self.params)

    # todo: this double roundtrip of parse/serialize html is ridiculous

    # remove all caditapp/email xmlns elements and attributes and non-inline css
    # note: use list() so that i can mutate the underlying object
    html = parseXml(html)
    def stripSpecial(el):
      for attr in list(el.keys()):
        if attr.startswith('{%s}' % (xmlns,)):
          del el.attrib[attr]
      for node in list(el.getchildren()):
        if node.tag.startswith('{%s}' % (xmlns,)):
          el.remove(node)
          continue
        stripSpecial(node)
    stripSpecial(html)
    for topnode in html.getchildren():
      if topnode.tag == '{%s}head' % (htmlns,):
        for node in list(topnode.getchildren()):
          if node.tag == '{%s}style' % (htmlns,) and node.get('type') == 'text/css':
            topnode.remove(node)

    style = (self.getTemplateStyle() or '').strip()
    if self.style is not None and len(self.style) > 0:
      style += self.style
    if len(style.strip()) > 0:
      html = inlineHtmlStyling(html, style)

    return serializeHtml(html)

  #----------------------------------------------------------------------------
  def inlineCidAttachments(self, html):
    # TODO: this is a "brute-force" approach... clean it up!
    atts = self.getAttachments()
    for att in atts:
      if not att.get('cid', False):
        continue
      # TODO: assuming PNG... inspect att['content-type']...
      value = 'data:image/png;base64,' + base64.b64encode(att['value'])
      html = html.replace('cid:' + att['name'], value)
    return html

  #----------------------------------------------------------------------------
  def getText(self):
    '''
    Returns the plain-text version of the email that would be
    generated if it were sent with the current settings. Use
    :meth:`send` to actually send the email.
    '''
    tpl = self.provider.getTemplate('text')
    if tpl is not None:
      return removeCids(reduce2ascii(tpl.render(**self.params)))
    html = self.getHtml()
    # todo: it would be interesting to be able to configure html2text to only
    #       put it footnotes for IMG tags that had non-"cid:" image references...
    text = html2text.html2text(html)
    # TODO: html2text should have taken care of this... but since it hasn't,
    #       are there any other characters that need to be escaped?...
    return removeCids(reduce2ascii(text))

  subject_collapse_spaces = re.compile(r'[\s]+', re.DOTALL)
  subject_remove_nonascii = re.compile(r'[^ -~]+', re.DOTALL)

  #----------------------------------------------------------------------------
  def getSubject(self):
    '''
    Returns the ``Subject`` header of the email that would be
    generated if it were sent with the current settings. Use
    :meth:`send` to actually send the email.
    '''
    tpl = self.provider.getTemplate('subject', self.template)
    # note: purposefully NOT using encoding=self.encoding so that i can
    #       then more cleanly replace HTML entity characters...
    # todo: clean up this entity-replacement strategy
    # todo: if no subject is found, the getText() version should be reduced
    #      and truncated...

    xdoc = parseXml(tpl.render(**self.params))
    etag = '{%s}subject' % (xmlns,)
    ret = []
    for node in xdoc.iter():
      if node.tag == etag or node.get(etag) == 'content':
        ret.append(node.text)
    ret = ' '.join(ret).encode('us-ascii', 'caditapp_email_unicode2ascii')
    ret = self.subject_collapse_spaces.sub(' ', ret)
    ret = self.subject_remove_nonascii.sub('', ret)
    if self.maxSubjectLength is not None and self.snipIndicator is not None:
      if len(ret) > self.maxSubjectLength:
        ret = ret[:self.maxSubjectLength - len(self.snipIndicator)] + self.snipIndicator
    return reduce2ascii(ret)

  #----------------------------------------------------------------------------
  def getProviderAttachments(self):
    # TODO: clean this up...
    if self.attachmentTable is None:
      self.attachmentTable = self.provider.getMap('attachments', {})
    return self.attachmentTable

  #----------------------------------------------------------------------------
  def getAttachments(self):
    atts = self.attachments[:]
    for att in self.getTemplateAttachments():
      if att['name'] not in [a['name'] for a in atts]:
        atts.append(att)
    for att in self.getProviderAttachments():
      if att['name'] not in [a['name'] for a in atts]:
        atts.append(att)
    return atts

  #----------------------------------------------------------------------------
  def getMimeAttachments(self):

    atts = self.getAttachments()

    # TODO: these attachments have been geared toward inlined image
    #       attachments... is this how standard attachments are sent as well?

    ret = []
    for adef in atts:
      # todo: a lot more escaping might need to be done here... especially of
      #       the attachment attributes...
      name  = adef['name']
      value = adef['value']
      ctype = adef.get('content-type', None) \
              or mimetypes.guess_type(name or '', False)[0] \
              or 'application/octet-stream'
      maintype, subtype = ctype.split('/', 1)
      if maintype == 'text':
        # Note: we should handle calculating the charset
        att = email.MIMEText.MIMEText(value, _subtype=subtype)
      elif maintype == 'image':
        att = email.MIMEImage.MIMEImage(value, _subtype=subtype, name=name)
      elif maintype == 'audio':
        att = email.MIMEAudio.MIMEAudio(value, _subtype=subtype)
      else:
        att = email.MIMEBase.MIMEBase(maintype, subtype)
        att.set_payload(value)
        email.Encoders.encode_base64(att)
      if adef.get('cid', False):
        att.add_header('Content-Disposition', 'attachment')
        att.add_header('Content-ID', '<' + name + '>')
      else:
        att.add_header('Content-Disposition', 'attachment', filename=name)
      ret.append(att)
    return ret

  #----------------------------------------------------------------------------
  def getOutputHeaders(self):
    curheaders = idict()
    curheaders.update(self.getTemplateHeaders())
    curheaders.update(self.headers)
    defaultHeaders = {
      'Subject':     lambda: self.getSubject(),
      }
    for name, call in defaultHeaders.items():
      if curheaders.has_key(name):
        continue
      curheaders[name] = call()
    if self.manager.updateHeaders is not None:
      self.manager.updateHeaders(self, curheaders)
    return curheaders

  #----------------------------------------------------------------------------
  def getSmtpData(self):
    '''
    Returns the raw SMTP data that would be sent if the email were sent
    with the current settings. Use :meth:`send` to actually send the email.
    '''
    return self._getSmtpData(self.getOutputHeaders())

  #----------------------------------------------------------------------------
  def _getSmtpData(self, curheaders):

    # TODO: is this the right structure for adding non-Content-ID attachments?...
    #       (e.g. boarding-pass style appt sheet)

    #  mail structure:
    #
    #     multipart/alternative
    #     |-- text/plain
    #     |-- multipart/related; type="text/html"
    #     |   |-- text/html
    #     |   `-- image/png... [attachments with "Content-ID"]
    #     `-- application/octet-stream... [attachments without "Content-ID"]
    #
    #               Content-Type: image/png
    #               Content-Transfer-Encoding: base64
    #               Content-Location: file:///.../...
    #               Content-ID: <ImageName>

    curheaders = idict(curheaders)

    # reduce headers to those that should be in outbound email
    # todo: should i instead be filtering for known allowed headers instead
    #       of removing known disallowed headers?...
    for header in ('bcc',):
      if curheaders.get(header):
        del curheaders[header]

    # the following text/html encoding selection is done only because
    # utf-8 results in base64 transfer encoding, which sucks because it
    # is not human-readable... hence trying others first. and the problem
    # with iso-8859-1 is that the "&copy;" and "&nbsp;" entities don't
    # show up, but it uses quoted-printable...
    # ==> UPDATE: i can't seem to reproduce this... the following translations
    #             occur: &mdash; => &#8212;, &copy; => &#169;, &nbsp; => &#160;

    # TODO: address the other self.encoding uses and see if the default
    #       should really be us-ascii instead of None...

    # encode the text-only alternative
    txtenc  = self.textEncoding or self.transferEncoding or self.encoding
    if txtenc is not None:
      txt = email.MIMEText.MIMEText(self.getText(), 'plain', txtenc)
    else:
      # do several encoding round trips until one is found that does not
      # degrade the content
      for txtenc in [ 'ascii', 'iso-8859-1', 'utf-8' ]:
        src = self.getText()
        try: txt = email.MIMEText.MIMEText(src, 'plain', txtenc)
        except UnicodeEncodeError: continue
        if src == txt.get_payload(decode=True):
          break

    # encode the html alternative
    htmlenc  = self.htmlEncoding or self.transferEncoding or self.encoding
    if htmlenc is not None:
      html = email.MIMEText.MIMEText(self.getHtml(), 'html', htmlenc)
    else:
      # do several encoding round trips until one is found that does not
      # degrade the content
      for htmlenc in [ 'ascii', 'iso-8859-1', 'utf-8' ]:
        src = self.getHtml()
        try: html = email.MIMEText.MIMEText(src, 'html', htmlenc)
        except UnicodeEncodeError: continue
        if src == html.get_payload(decode=True):
          break

    # and now stitch all the parts together

    mbound  = self.boundary and ( '==' + self.boundary + '==' ) or None
    msg = email.MIMEMultipart.MIMEMultipart('alternative', boundary=mbound)

    rbound  = self.boundary and ( '==' + self.boundary + '-related==' ) or None
    related = email.MIMEMultipart.MIMEMultipart('related', boundary=rbound)

    if 'text' in self.include:
      msg.attach(txt)

    if 'html' in self.include:
      related.attach(html)
      msg.attach(related)

    if 'attachments' in self.include:
      for att in self.getMimeAttachments():
        if 'Content-ID' in att.keys():
          related.attach(att)
        else:
          msg.attach(att)

    if self.include == ['text']:
      for k,v in curheaders.items():
        txt[smtpHeaderFormat(k)] = v
      return txt.as_string()

    for k,v in curheaders.items():
      msg[smtpHeaderFormat(k)] = v

    return msg.as_string()

  #----------------------------------------------------------------------------
  def send(self, mailfrom=None, recipients=None):
    '''
    Send the email. The ``To`` header can be overriden with the `recipients`
    parameter, and the ``From`` header con be overriden with the `mailfrom`
    parameter. Note that if these parameters are used, then the headers are
    NOT adjusted to reflect the new settings (this is to allow ``Bcc`` type
    behavior).

    Parameters:

    :param mailfrom:

      string, email address to set as the ``MAIL FROM`` address on the
      SMTP protocol level. Note that this will NOT set or override the
      active ``From`` header. If not specified, the address will be
      extracted from the ``From`` header.

    :param recipients:

      string or list-of-string, email addresses to send this email to,
      on the SMTP protocol level. Note that this will NOT set or
      override the active ``To`` header. If not specified, the
      addresses will be extracted from the ``To``, ``CC``, and ``BCC``
      headers.
    '''
    hdrs = self.getOutputHeaders()
    if mailfrom is None:
      mailfrom = extractEmails(hdrs.get('from'))
      if not mailfrom:
        raise MissingHeader('email source ("from") not specified')
      mailfrom = mailfrom[0]
    if recipients is None:
      recipients = extractEmails(hdrs.get('to')) or []
      recipients += extractEmails(hdrs.get('cc')) or []
      recipients += extractEmails(hdrs.get('bcc')) or []
      if not recipients or len(recipients) <= 0:
        raise MissingHeader('email destination ("to") not specified')
    elif isinstance(recipients, basestring):
      recipients = [recipients]
    if hasattr(self.manager, 'updateRecipients'):
      recipients = self.manager.updateRecipients(self, recipients)
    if hasattr(self.manager, 'updateMailfrom'):
      mailfrom = self.manager.updateMailfrom(self, mailfrom)
    self.manager.sender.send(mailfrom, recipients, self._getSmtpData(hdrs))

#------------------------------------------------------------------------------
# end of $Id$
#------------------------------------------------------------------------------
