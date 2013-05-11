#!/usr/bin/env python

# @package Tld
# @author Artur Barseghyan (artur.barseghyan@gmail.com)
# @version 0.1
# @license MPL 1.1/GPL 2.0/LGPL 2.1
# @link http://bitbucket.org/barseghyanartur/php-tld
#
# Commands for updating the TLD names file from command line.

from tld.utils import update_tld_names

_ = lambda x: x

if __name__ == '__main__':
    update_tld_names()
    print _("Local TLD names file has been successfully updated!")
