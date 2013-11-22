# Copyright 2013 semantics GmbH
# Written by Marcus Brinkmann <m.brinkmann@semantics.de>

from __future__ import print_function, division
from __future__ import absolute_import, unicode_literals

import itertools
from collections import OrderedDict
import re
from copy import deepcopy
from contextlib import contextmanager

from lxml import etree

import sys

from grako.exceptions import FailedSemantics
from grako.ast import AST

from . mw import mwParser as Parser
from . html import entity_by_name, attribute_whitelist, css_filter, escape_id
from . html import ITER_PUSH, ITER_POP, ITER_ADD, iter_structure
from . settings import Settings


def extract_section(root, section):
    start = None
    stop = None
    structure = iter_structure(root)
    if section == 0:
        # Take the head part (before any section).
        while True:
            try:
                action, _, el = next(structure)
            except StopIteration:
                break
            if action == ITER_ADD:
                stop = el
                break
    else:
        idx = 0
        while True:
            try:
                action, _, el = next(structure)
            except StopIteration:
                break
            if action == ITER_ADD:
                idx = idx + 1
                if idx == section:
                    break
        if start is None:
            return None

        # Looking for the end of the section.  After ITER_ADD for
        # start, we may have a PUSH/POP block, followed by optional
        # POP actions, followed by ADD (or end of list).  Note that
        # there can't be another PUSH action before the ADD (every
        # section has at most one list of subsections).
        idx = 0
        while True:
            try:
                action, toc_nrs, el = next(structure)
            except StopIteration:
                break
            if action == ITER_PUSH:
                # Can only happen once immediately after seeing start.
                while True:
                    try:
                        _, more_toc_nrs, _ = next(structure)
                    except StopIteration:
                        break
                        if more_toc_nrs == toc_nrs:
                            break
            elif action == ITER_POP:
                # There may be pop actions before the next add.
                pass
            elif action == ITER_ADD:
                stop = el
                break

    # Extract everything between start and stop.
    
    ident_nr = 0
    while True:
        action, _, el = structure.next()
        if action == ITER_ADD:
            ident_nr = ident_nr + 1
            if 
    for action, toc_nrs, el in structure:
        if action == ITER_ADD:
            ident_nr = ident_nr + 1
            if ident_nr == section:
                start = el
            elif ident_nr == sec
                
            span = el[0]
            ident = span.get("id")
            if ident in ids:
                nr = ids[ident] + 1
                ids[ident] = nr
                span.set("id", ident + "_" + str(nr))
            else:
                ids[ident] = 1
    
