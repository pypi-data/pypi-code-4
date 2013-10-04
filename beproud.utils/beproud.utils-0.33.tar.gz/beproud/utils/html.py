# vim:fileencoding=utf-8
import re
import string

__all__ = (
    'escape',
    'escape_entities',
    'sanitize_html',
    'urlize',

    'URL_VALID_CHARS',
    'URL_PATH_VALID_CHARS',
    'URL_QUERY_VALID_CHARS',
    'URL_FRAGMENT_VALID_CHARS',

    'DOMAIN_RE',
    'PORT_RE',
    'IP_ADDRESS_RE',
    'IP_PORT_RE',
    'IP_DOMAIN_RE',
    'URL_DOMAIN_RE',
    'URL_RE',
    'URL_RE_CMP',

    'LOOSE_DOMAIN_RE',
    'LOOSE_PORT_RE',
    'LOOSE_URL_RE',
    'LOOSE_URL_RE_CMP',
)

# Monkey-patch HTMLParser to allow parsing of html
# attributes whose values have no quotes and are non-ascii
# i.e. <input name=submit type=submit value=検索>
import HTMLParser
try:
    _p = HTMLParser.HTMLParser()
    _p.feed(u"<input name=submit type=submit value=検索>")
    _p.close()
except HTMLParser.HTMLParseError:
    # Only patch HTMLParser if it's needed.
    HTMLParser.attrfind = re.compile(
        r'\s*([a-zA-Z_][-.:a-zA-Z_0-9]*)(\s*=\s*'
        r'(\'[^\']*\'|"[^"]*"|[^">\s]*))?')

try: 
    from django.utils.html import escape
except ImportError:
    from strutils import force_unicode
    def escape(html):
        """
        Returns the given HTML with ampersands, quotes and angle brackets encoded.
        """
        return force_unicode(html).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#39;')

def escape_entities(text):
        return re.sub(r'&(?![A-Za-z]+;)', '&amp;', text)\
                 .replace('<','&lt;')\
                 .replace('>', '&gt;')\
                 .replace('"', '&quot;')\
                 .replace("'", '&apos;')

DEFAULT_VALID_TAGS = {
    'b': (),
    'blockquote': ('style',),
    'em': (),
    'strong': (),
    'strike': (),
    'a': ('href', 'title', 'rel'),
    'i': (),
    'br': (),
    'ul': (),
    'ol': (),
    'li': (),
    'u': (),
    'p': (),
    'h1': (),
    'h2': (),
    'h3': (),
    'h4': (),
    'table': (),
    'thead': (),
    'tbody': (),
    'tfoot': (),
    'th': (),
    'td': ('colspan',),
    'tr': ('rowspan',),
    'hr': (),
    'img': ('src', 'alt', 'title', 'width', 'height', 'align'),
    'span': ('style',),
    'div': ('style',),
    'font': ('size', 'style', 'color'),
}

DEFAULT_VALID_STYLES = (
    "background-color",
    "color",
    "margin",
    "margin-left",
    "margin-right",
    "border",
    "padding",
    "font-weight",
    "font-style",
    "font-size",
    "text-align",
    "text-decoration",
)

HTTP_SCHEME_RE = 'http[s]*'

# See: http://www.ietf.org/rfc/rfc1738.txt
URL_SAFE = "$-_.+"
URL_EXTRA = "!*'(),"
URL_PATH_RESERVED = ';?'
URL_QUERY_RESERVED = '#'
URL_OTHER_RESERVED = ':@&=/'
URL_RESERVED = URL_PATH_RESERVED + URL_QUERY_RESERVED + URL_OTHER_RESERVED
URL_ESCAPE = '%'
URL_ALNUM = string.letters + string.digits

URL_VALID_CHARS = URL_ALNUM + URL_SAFE + URL_EXTRA + URL_RESERVED + URL_ESCAPE
URL_PATH_VALID_CHARS = URL_ALNUM + URL_SAFE + URL_EXTRA + URL_OTHER_RESERVED + URL_ESCAPE
URL_QUERY_VALID_CHARS = URL_ALNUM + URL_SAFE + URL_EXTRA + URL_OTHER_RESERVED + URL_PATH_RESERVED + URL_ESCAPE
URL_FRAGMENT_VALID_CHARS = URL_ALNUM + URL_SAFE + URL_EXTRA + URL_RESERVED + URL_ESCAPE


# 0-65535
# See: http://www.regular-expressions.info/numericranges.html 
PORT_RE = "%s" % "|".join([
    "6553[0-5]",
    "655[0-2][0^9]",
    "65[0-4][0-9][0-9]",
    "6[0-4][0-9][0-9][0-9]",
    "[1-5][0-9][0-9][0-9][0-9]",
    "[1-9][0-9][0-9][0-9]",
    "[1-9][0-9][0-9]",
    "[1-9][0-9]",
    "[1-9]",
])

# See: http://www.shauninman.com/archive/2006/05/08/validating_domain_names
# See: http://www.iana.org/domains/root/db/
DOMAIN_RE = '(?:[a-z0-9](?:[-a-z0-9]*[a-z0-9])?\\.)+(?:(?:aero|arpa|a[cdefgilmnoqrstuwxz])|(?:cat|com|coop|b[abdefghijmnorstvwyz]|biz)|(?:c[acdfghiklmnorsuvxyz])|d[ejkmoz]|(?:edu|e[ceghrstu])|f[ijkmor]|(?:gov|g[abdefghilmnpqrstuwy])|h[kmnrtu]|(?:info|int|i[delmnoqrst])|(?:jobs|j[emop])|k[eghimnprwyz]|l[abcikrstuvy]|(?:mil|mobi|museum|m[acdghklmnopqrstuvwxyz])|(?:name|net|n[acefgilopruz])|(?:om|org)|(?:pro|p[aefghklmnrstwy])|qa|r[eouw]|s[abcdeghijklmnortvyz]|(?:travel|t[cdfghjklmnoprtvwz])|u[agkmsyz]|v[aceginu]|w[fs]|y[etu]|z[amw])'
# Domain with port number
DOMAIN_PORT_RE = '(%s)(?::(%s))?' % (DOMAIN_RE, PORT_RE)

# See: http://www.regular-expressions.info/regexbuddy/ipaccurate.html
IP_ADDRESS_RE = '(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)'
# IP address with port number
IP_PORT_RE = '(%s)(?::(%s))?' % (IP_ADDRESS_RE, PORT_RE)

# Domain or IP address
IP_DOMAIN_RE = '(%s)|(%s)' % (DOMAIN_RE, IP_ADDRESS_RE)

# Domain or IP address with port number
URL_DOMAIN_RE = '(?:%s)(?::(%s))?' % (IP_DOMAIN_RE, PORT_RE)
URL_RE = r'(%s)\:\/\/(%s)(/[%s]*)?(?:\?([%s]*))?(?:\#([%s]*))?' % (
    HTTP_SCHEME_RE,
    URL_DOMAIN_RE,
    re.escape(URL_PATH_VALID_CHARS),
    re.escape(URL_QUERY_VALID_CHARS),
    re.escape(URL_FRAGMENT_VALID_CHARS),
)
URL_RE_CMP = re.compile(URL_RE)

LOOSE_DOMAIN_RE = r"(?:localhost|[\w-]+\.[\w-]+(?:\.[\w-]+)*)"
LOOSE_PORT_RE = "\d+"
LOOSE_URL_RE = r'(%s)\:\/\/(%s)/([%s]*)(?:\?([%s]*))?(?:\#([%s]*))?' % (
    HTTP_SCHEME_RE,
    '(?:(%s)|(%s))(?::(%s))?' % (LOOSE_DOMAIN_RE, IP_ADDRESS_RE, LOOSE_PORT_RE),
    re.escape(URL_PATH_VALID_CHARS),
    re.escape(URL_QUERY_VALID_CHARS),
    re.escape(URL_FRAGMENT_VALID_CHARS),
)
LOOSE_URL_RE_CMP = re.compile(LOOSE_URL_RE)

def sanitize_html(htmlSource, encoding=None, type="text/html", valid_tags=DEFAULT_VALID_TAGS, valid_styles=DEFAULT_VALID_STYLES, add_nofollow=False):
    """
    Clean bad html content. Currently this simply strips tags that
    are not in the VALID_TAGS setting.
    
    This function is used as a replacement for feedparser's _sanitizeHTML
    and fixes problems like unclosed tags and gives finer grained control
    over what attributes can appear in what tags.

    Returns the sanitized html content.

    encoding is the encoding of the htmlSource

    type is the mimetype of the content. It is ignored and is present only
    for compatibility with feedparser. 

    valid_tags is a dictionary containing keys of valid tag names which
    have a value that is a list of valid attribute names. An empty list
    indicates that no attributes are allowed. A value of None indicates
    that all attributes are allowed.

    valid_styles is a list of valid css styles that can be included in
    style tags. Style names that are not included in this list are
    stripped from the html content.

    add_nofollow can be provided which can either be a boolean value
    or a regex that can be matched against a url. If the regex matches
    then nofollow is added to the url.
    """
    from BeautifulSoup import BeautifulSoup, Comment

    js_regex = re.compile(r'[\s]*(&#x.{1,7})?'.join(list('javascript')))
    # Sanitize html with BeautifulSoup
    if encoding:
        soup = BeautifulSoup(htmlSource, fromEncoding=encoding)
    else:
        soup = BeautifulSoup(htmlSource)

    def entities(text):
        return text.replace('<','&lt;')\
                   .replace('>', '&gt;')\
                   .replace('"', '&quot;')\
                   .replace("'", '&apos;')
    
    # Sanitize html text by changing bad text to entities.
    # BeautifulSoup will do this for href and src attributes
    # on anchors and image tags but not for text.
    for text in soup.findAll(text=True):
        text.replaceWith(entities(text))

    # コメントを削る
    for comment in soup.findAll(text=lambda text: isinstance(text, Comment)):
        comment.extract()

    for tag in soup.findAll(True):
        if tag.name not in valid_tags:
            tag.hidden = True
        else:
            tag.attrs = [(attr, js_regex.sub('', val))
                            for attr, val in tag.attrs 
                            if attr in valid_tags[tag.name]]

    # Add rel="nofollow" links
    if add_nofollow:
        findall_kwargs = {}
        if not isinstance(add_nofollow, bool):
            findall_kwargs["attrs"] = {"href": add_nofollow}
        for tag in soup.findAll("a", **findall_kwargs):
            rel = tag.get('rel', '').split()
            if 'nofollow' not in rel:
                rel.append('nofollow')
                tag['rel'] = ' '.join(rel)

    # Clean up CSS style tags
    for tag in soup.findAll(attrs={"style":re.compile(".*")}):
        old_styles = [s.strip() for s in tag["style"].split(";")]

        # style_order preserves uniqueness 
        styles = {}
        # style_order preserves order
        style_order=[]
        for style in old_styles:
            if ':' in style:
                style_name, style_value = style.split(':', 1)
                # Style names are case insensitive so
                # change to lowercase
                style_name = style_name.strip().lower()
                if style_name in valid_styles:
                    style_value = style_value.strip()
                    if style_name in styles:
                        styles[style_name] = style_value
                        style_order.remove(style_name)
                        style_order.append(style_name)
                    else:
                        styles[style_name] = style_value
                        style_order.append(style_name)

        if styles:
            tag["style"] = ';'.join([('%s:%s' % (s, styles[s])) for s in style_order]) + ';'
        else:
            del tag["style"]

    # Sanitize html text by changing bad text to entities.
    # BeautifulSoup will do this for href and src attributes
    # on anchors and image tags but not for text.
    for text in soup.findAll(text=True):
        text.replaceWith(escape_entities(text))

    return soup.renderContents().decode('utf8') 

URLIZE_TMPL = '<a href="%(link_url)s"%(attrs)s>%(link_text)s</a>'
def urlize(text, trim_url_limit=None, attrs={}, url_re=URL_RE_CMP, autoescape=False):
    """text内URLを抽出してアンカータグで囲む
    
    URLのデリミタは半角カンマ、<>(エスケープ済み含む)、\s、全角スペース、行末で、これらが末尾にマッチしない場合はURLとして認識しません。
    URL部分は.+の最小マッチ、もしくはtrim_url_limitが指定された場合は{,trim_url_limit}の最小マッチとなります。

    -args

        text:           urlize対象文字列
        trim_url_limit: urlとして認識する文字数に上限を設ける場合は数値をセット
        nofollow:       Trueを与えるとタグにrel="nofollow"を付加
        autoescape:     Trueを与えるとタグエスケープを行います。
    
    """
    from strutils import abbrev

    if autoescape:
        text = escape(text)

    def _repl(m):
        return URLIZE_TMPL % {
            "link_url": m.group(),
            "attrs": "".join(map(lambda x: ' %s="%s"' % x, attrs.iteritems())),
            "link_text": abbrev(m.group(), trim_url_limit) if trim_url_limit is not None else m.group(),
        }

    return url_re.sub(_repl, text)
