# -*- coding: utf-8 -*-
#
# File: wfsubscribers.py
#
# Copyright (c) 2009 by []
# Generator: ArchGenXML Version 2.2 (svn)
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#

__author__ = """Michael Launay <michaellaunay@ecreall.com>"""
__docformat__ = 'plaintext'


##code-section module-header #fill in your manual code here
##/code-section module-header


def doFinish(obj, event):
    """generated workflow subscriber."""
    # do only change the code section inside this function.
    if not event.transition \
       or event.transition.id not in ['finish'] \
       or obj != event.object:
        return
    ##code-section doFinish #fill in your manual code here
    event.object.doFinish(event)
    ##/code-section doFinish


def doCancel(obj, event):
    """generated workflow subscriber."""
    # do only change the code section inside this function.
    if not event.transition \
       or event.transition.id not in ['cancel', 'abort'] \
       or obj != event.object:
        return
    ##code-section doCancel #fill in your manual code here
    event.object.doCancel(event)
    ##/code-section doCancel


def doRun(obj, event):
    """generated workflow subscriber."""
    # do only change the code section inside this function.
    if not event.transition \
       or event.transition.id not in ['run_again', 'run', 'resume'] \
       or obj != event.object:
        return
    ##code-section doRun #fill in your manual code here
    event.object.doRun(event)
    ##/code-section doRun


def doSuspend(obj, event):
    """generated workflow subscriber."""
    # do only change the code section inside this function.
    if not event.transition \
       or event.transition.id not in ['supsend'] \
       or obj != event.object:
        return
    ##code-section doSuspend #fill in your manual code here
    event.object.doSuspend(event)
    ##/code-section doSuspend



##code-section module-footer #fill in your manual code here
##/code-section module-footer

