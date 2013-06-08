#!/usr/bin/env python

import argparse
import bs4
import html2text
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


def main():
    parser = argparse.ArgumentParser(description='Displays nicely-formatted PHP documentation')
    parser.add_argument('symbol', help='PHP symbol')
    parser.add_argument('--ascii', help='attempt to convert output to ASCII',
                        action='store_true')

    args = parser.parse_args()

    text = formatted_reference(normalised_html(reference_html(args.symbol)))
    print (asciify(text) if args.ascii else text)


if __name__ == '__main__':
    main()
