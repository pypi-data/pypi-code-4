# vim:fileencoding=utf-8

from random import sample

__all__ = (
    'StrAndUnicode',
    'force_unicode',
    'smart_str',
    'trim',
    'force_int',
    'make_random_key',
    'abbrev',
)

try:
    from django.utils.encoding import StrAndUnicode, force_unicode, smart_str
except ImportError:
    import types
    import datetime
    from decimal import Decimal

    class StrAndUnicode(object):
        """
        A class whose __str__ returns its __unicode__ as a UTF-8 bytestring.

        Useful as a mix-in.
        """
        def __str__(self):
            return self.__unicode__().encode('utf-8')

    def is_protected_type(obj):
        """Determine if the object instance is of a protected type.

        Objects of protected types are preserved as-is when passed to
        force_unicode(strings_only=True).
        """
        return isinstance(obj, (
            types.NoneType,
            int, long,
            datetime.datetime, datetime.date, datetime.time,
            float, Decimal)
        )

    def force_unicode(s, encoding='utf-8', strings_only=False, errors='strict'):
        """
        Similar to smart_unicode, except that lazy instances are resolved to
        strings, rather than kept as lazy objects.

        If strings_only is True, don't convert (some) non-string-like objects.
        """
        if strings_only and is_protected_type(s):
            return s
        if not isinstance(s, basestring,):
            if hasattr(s, '__unicode__'):
                s = s.__unicode__()
            else:
                try:
                    s = unicode(str(s), encoding, errors)
                except UnicodeEncodeError:
                    if not isinstance(s, Exception):
                        raise
                    # If we get to here, the caller has passed in an Exception
                    # subclass populated with non-ASCII data without special
                    # handling to display as a string. We need to handle this
                    # without raising a further exception. We do an
                    # approximation to what the Exception's standard str()
                    # output should be.
                    s = ' '.join([force_unicode(arg, encoding, strings_only,
                            errors) for arg in s])
        elif not isinstance(s, unicode):
            # Note: We use .decode() here, instead of unicode(s, encoding,
            # errors), so that if s is a SafeString, it ends up being a
            # SafeUnicode at the end.
            s = s.decode(encoding, errors)
        return s

    def smart_str(s, encoding='utf-8', strings_only=False, errors='strict'):
        """
        Returns a bytestring version of 's', encoded as specified in 'encoding'.

        If strings_only is True, don't convert (some) non-string-like objects.
        """
        if strings_only and isinstance(s, (types.NoneType, int)):
            return s
        elif not isinstance(s, basestring):
            try:
                return str(s)
            except UnicodeEncodeError:
                if isinstance(s, Exception):
                    # An Exception subclass containing non-ASCII data that doesn't
                    # know how to print itself properly. We shouldn't raise a
                    # further exception.
                    return ' '.join([smart_str(arg, encoding, strings_only,
                            errors) for arg in s])
                return unicode(s).encode(encoding, errors)
        elif isinstance(s, unicode):
            return s.encode(encoding, errors)
        elif s and encoding != 'utf-8':
            return s.decode('utf-8', errors).encode(encoding, errors)
        else:
            return s

def trim(s, encoding="utf-8"):
    """
    全角・半角も含めてトリミング
    """
    return force_unicode(s, encoding).strip()

def force_int(num, default=None):
    try:
        return int(num)
    except (ValueError, TypeError):
        return default

def make_random_key(size=128, values=None):
    if values is None:
        import string
        values = string.letters + string.digits
    keys = ""
    src = list(values)
    while True:
        diff = size - len(keys)
        if diff <= 0:
            break
        keys += "".join(sample(src, (diff < 20 and diff or 20)))
    return keys

def abbrev(s, num=255, end="..."):
    """
    文章を要約する
    質問の文章などで利用

    返す文字列の長さは、num以上にならないのを保証します。

    >>> abbrev('spamspamspam', 6)
    'spa...'
    >>> abbrev('spamspamspam', 12)
    'spamspamspam'
    >>> abbrev('blahblahblah', 13)
    'eggseggseg...'
    >>> abbrev('eggseggseggs', 1)
    'e'
    >>> abbrev('eggseggseggs', 2, '.')
    'e.'
    """
    index = num - len(end)
    if len(s) > num:
        s = (s[:index] + end) if index > 0 else s[:num]
    return s
