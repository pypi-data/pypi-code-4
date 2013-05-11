#!/usr/bin/env python

# @package Tld
# @author Artur Barseghyan (artur.barseghyan@gmail.com)
# @version 0.1
# @license MPL 1.1/GPL 2.0/LGPL 2.1
# @link http://bitbucket.org/barseghyanartur/php-tld
#
# Tld tests/examples

from tld.utils import get_tld

_ = lambda x: x

if __name__ == '__main__':
    # Testing good patterns
    for url in ['http://www.google.co.uk', 'http://www.v2.google.co.uk', 'http://www.me.congresodelalengua3.ar']:
        print '******** Testing the URL: %s' % url
        print get_tld(url)

    # Testing the bad patterns
    for url in ['/index.php?a=1&b=2', 'v2.www.google.com', 'http://www.tld.doesnotexist']:
        print '******** Testing the URL: %s' % url
        try:
            print get_tld(url)
        except Exception, e:
            print e
