#!/usr/bin/env python

import argparse
import bs4
import codecs
import html2text
import os.path
import re
import unicodedata
import urllib2


def reference_html(php_symbol):
    """
    Fetches reference HTML for a PHP built-in. The documentation is loaded
    from http://php.net.
    """
    url = 'http://php.net/%s' % php_symbol
    return urllib2.urlopen(url).read()


def normalised_html(html):
    """
    Extracts (and transforms) relevant parts of an HTML string.
    """
    soup = bs4.BeautifulSoup(html)
    root = soup.find(attrs='refentry')

    # Format function signature
    synopsis = root.find(attrs='methodsynopsis')
    pre = soup.new_tag('pre')
    pre.append(re.sub('\s+', ' ', synopsis.get_text().strip()))
    synopsis.replace_with(pre)

    # Remove unwanted information
    changelog = root.find(attrs='changelog')
    if changelog: changelog.decompose()

    # Remove misused/unnecessary <blockquote>s
    for tag in root.find_all('blockquote'):
        tag.unwrap()

    # Convert <h3> => <h2>
    for h3 in root.find_all('h3'):
        h2 = soup.new_tag('h2')
        h2.append(h3.get_text().strip())
        h3.replace_with(h2)

    # Unwrap decorated <code> elements. Markdown looks a bit noisy when
    # different formatting elements are combined (e.g. **`foo`**)
    for code in root.find_all('code'):
        if code.parent.name in ('em', 'strong'):
            code.parent.unwrap()

    # Convert block <code> => <pre>
    for code in [div.find('code') for div in root.find_all('div', 'phpcode')]:
        for br in code.find_all('br'):
            br.replace_with('\n')
        pre = soup.new_tag('pre')
        pre.append(code.get_text().strip())
        code.replace_with(pre)

    return unicode(root)


def formatted_reference(html):
    """
    Converts an HTML string to Markdown.
    """
    converter = html2text.HTML2Text()
    converter.ignore_links = True
    converter.body_width = 0

    text = converter.handle(html)
    text = re.sub(' +$', '', text, flags=re.MULTILINE)
    text = re.sub(r'\n\n+', '\n\n', text, flags=re.MULTILINE)
    return text


def asciify(s):
    """
    Returns the approximate ASCII equivalent of a Unicode string.
    """
    # http://en.wikipedia.org/wiki/Unicode_equivalence#Normal_forms
    return unicodedata.normalize('NFKD', s).encode('ascii', 'ignore')


class FileSystemCache(object):

    def __init__(self, path):
        path = os.path.expanduser(path)
        if not os.path.isdir(path):
            raise Exception('Cache directory %s not found' % path)
        self.path = path

    def get(self, php_symbol):
        try:
            with codecs.open(self._resolve_path(php_symbol), 'r', 'utf-8') as f:
                return f.read()
        except IOError:
            return None

    def put(self, php_symbol, contents):
        with codecs.open(self._resolve_path(php_symbol), 'w', 'utf-8') as f:
            f.write(contents)

    def _resolve_path(self, php_symbol):
        return os.path.join(self.path, php_symbol)


class BlackHoleCache(object):
    def get(self, php_symbol): pass
    def put(self, php_symbol, contents): pass


def main():
    parser = argparse.ArgumentParser(description='Displays nicely-formatted PHP documentation')
    parser.add_argument('symbol', help='PHP symbol')
    parser.add_argument('--ascii', help='attempt to convert output to ASCII', action='store_true')
    parser.add_argument('--cache', help='local HTML cache directory', metavar='<dir>')

    args = parser.parse_args()

    cache = FileSystemCache(args.cache) if args.cache else BlackHoleCache()
    text = cache.get(args.symbol)
    if not text:
        text = formatted_reference(normalised_html(reference_html(args.symbol)))
        cache.put(args.symbol, text)

    print (asciify(text) if args.ascii else text)


if __name__ == '__main__':
    main()
