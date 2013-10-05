#!/usr/bin/env python
""" Command line interface to difflib.py providing diffs in unified_diff format:

"""
from __future__ import print_function, unicode_literals
from __future__ import absolute_import, division
import re
import bisect
import shutil, fnmatch

try:
    from os.path import relpath
except ImportError: # python < 2.6
    from os.path import curdir, abspath, sep, commonprefix, pardir, join
    def relpath(path, start=curdir):
        """Return a relative version of a path"""
        if not path:
            raise ValueError("no path specified")
        start_list = abspath(start).split(sep)
        path_list = abspath(path).split(sep)
        # Work out how much of the filepath is shared by start and path.
        i = len(commonprefix([start_list, path_list]))
        rel_list = [pardir] * (len(start_list)-i) + path_list[i:]
        if not rel_list:
            return curdir
        return join(*rel_list)

def add2list(lst, item):
    """Add item to lst if not already present using bisect to maintain order."""
    try:
        i = bisect.bisect_left(lst, item)
    except:
        print("error adding", item, "\n    ", lst[-1])
        return()

    if i != len(lst) and lst[i] == item:
        return()
    bisect.insort(lst, item)



item_regex = re.compile(r'^([\+\-\~\?\=\%\$\*X])\s+(.*)\s*$')
at_regex = re.compile(r'^\s*@@\s*\-([\d,]+)\s*\+([\d,]+)\s*@@.*$')
    # r'^\s*@@\s*\-([\d,]+)\s*\+([\d,]+)\YPs*@@\s*([a-z0-9\-]{36})?\s*$')
id_regex = re.compile(r'^\s*\+?@i\s*([a-z0-9\-]{36})\s*$')
# id_regex = re.compile(r"@i\s+\+?[a-z0-9]{8}\-[a-z0-9]{4}\-[a-z0-9]{4}\-[a-z0-9]{4}\-[a-z0-9]{12}\b")


default_regex = re.compile(r'^\s*\=\s*(.*)\s*$')
group_regex = re.compile(r'^\s*\+\s*(.*)\s*$')
junk_regex = re.compile(r"\s*$")
timestamp_regex = re.compile(r'^###\s+([0-9\-\:\s]{16})\s+###\s*$')

junk = ' '

def IS_LINE_JUNK(s):
    return(junk_regex.match(s))


import sys, os, difflib
from difflib import SequenceMatcher

# print(difflib.unified_diff.__doc__)

from datetime import datetime
rfmt="%Y-%m-%d %H:%M"
now = datetime.now().strftime(rfmt)

#!/usr/bin/env python

import os, sys, struct, stat
import difflib
import re
from optparse import OptionParser
# from mercurial.bdiff import bdiff, blocks


def my_diff(a, b, fromfile='', tofile='', fromfiledate='',
                 tofiledate='', n=0, lineterm='\n'):
    started = False
    for group in SequenceMatcher(isjunk=IS_LINE_JUNK, a=a,
            b=b).get_grouped_opcodes(n):
        if not started:
            yield '--- %s %s%s' % (fromfile, fromfiledate, lineterm)
            yield '+++ %s %s%s' % (tofile, tofiledate, lineterm)
            started = True
        i1, i2, j1, j2 = group[0][1], group[-1][2], group[0][3], group[-1][4]
        maybe = "@@ -%d,%d +%d,%d @@%s" % (i1+1, i2-i1, j1+1, j2-j1, lineterm)
        for tag, i1, i2, j1, j2 in group:
            if tag == 'equal':
                for line in a[i1:i2]:
                    if not IS_LINE_JUNK(line):
                        if maybe:
                            yield maybe
                            maybe = ''
                        yield ' ' + line
                continue
            if tag == 'replace' or tag == 'delete':
                for line in a[i1:i2]:
                    if not IS_LINE_JUNK(line):
                        if maybe:
                            yield maybe
                            maybe = ''
                        yield '-' + line
            if tag == 'replace' or tag == 'insert':
                for line in b[j1:j2]:
                    if not IS_LINE_JUNK(line):
                        if maybe:
                            yield maybe
                            maybe = ''
                        yield '+' + line

def filediff(fromfile, tofile, ndiff=False):
    fo = open(fromfile, 'r')
    fromlines = fo.readlines()
    fo.close()
    fo = open(tofile, 'r')
    tolines = fo.readlines()
    fo.close()
    outlines = diff(fromlines, tolines, ndiff)
    return(outlines)

def diff(fromlines, tolines, ndiff=False):
    fromlines = [x.rstrip() for x in fromlines]
    tolines = [x.rstrip() for x in tolines]
    outlines = []

    fromIds = []
    fromuuids = {}
    current_default = -1
    current_group = -1
    # fromgroups = {}
    for i in range(len(fromlines)):
        m = id_regex.match(fromlines[i])
        if m:
            # print('from id match', fromlines[i])
            fromuuids[i] = m.group(1)
            fromIds.append(i)
            if current_default >= 0:
                # fromlines[i] += "; defaults: %s" % default_value
                # fromlines[i] += ""
                pass
            if current_group >= 0:
                # fromlines[i] += "; group: %s" % group_value
                # fromlines[i] += ""
                pass


        m = default_regex.match(fromlines[i])
        if m:
            current_default = i
            default_value = m.group(1)
            fromlines[i] = junk
        m = item_regex.match(fromlines[i])
        if m:
            if m.group(1) == '+':
                if current_group < 0:
                    # we are beginning a group
                    current_group = i
                    group_value = m.group(2)
                    fromlines[i] = junk
                    # print("got group_value", group_value)
            else:
                # we are not in or have left a group
                current_group = -1

    toIds = []
    touuids = {}
    current_default = -1
    current_group = -1
    # togroups = {}
    for i in range(len(tolines)):
        m = id_regex.match(tolines[i])
        if m:
            # print('to id match', tolines[i])
            touuids[i] = m.group(1)
            toIds.append(i)
            if current_default >= 0:
                # tolines[i] += "; defaults: %s" % default_value
                pass
            if current_group >= 0:
                # print(current_default, "provides defaults for", i)
                # tolines[i] += "; group: %s" % group_value
                pass

        m = default_regex.match(tolines[i])
        if m:
            current_default = i
            default_value = m.group(1)
            tolines[i] = junk

        m = item_regex.match(tolines[i])
        if m:
            if m.group(1) == '+':
                if current_group < 0:
                    # we are beginning a group
                    current_group = i
                    group_value = m.group(2)
                    tolines[i] = junk
                    # print("got group_value", group_value)
            else:
                # we are not in or have left a group
                current_group = -1

    if ndiff:
        difflines = list(difflib.ndiff(fromlines, tolines))
        if not difflines:
            return()
    else:
        # difflines = list(difflib.unified_diff(fromlines, tolines, n=0))
        difflines = list(my_diff(fromlines, tolines))
        if not len(difflines) > 2:
            return()
        difflines = difflines[2:]

    # print("\ndifflines")
    # print("\n".join([x.strip() for x in difflines]))

    changed_ids = set([])
    # print('from/to', fromIds, toIds)

    # sys.stdout.write("### %s ###\n" % (now))
    outlines.append("### %s ###" % (now))

    # print("fromIds", fromIds)
    # print("toIds", toIds)
    for line in difflines:
        # print("diff line", line)
        l1 = line[0]
        if l1 == '?':
            l2 = line[2:]
        else:
            l2 = line[1:].strip()
        m = at_regex.match(line)
        if m:
            changed_ids = set([])
            minus = map(int, m.group(1).split(','))
            plus = map(int, m.group(2).split(','))
            # print("matched", minus, plus, line)
            minusId = None
            plusId = None
            if len(minus) == 1 or minus[1] > 0:
                # we need the id for minus
                idline = bisect.bisect_left(fromIds, minus[0])
                # print("minus idline", idline, 'for', minus[0])
                # print("fromids", idline,
                #     fromIds[idline],
                #     fromlines[fromIds[idline]],
                #     fromuuids[fromIds[idline]])
                # print("adding to changed from", fromuuids[fromIds[idline]])
                changed_ids.add(fromuuids[fromIds[idline]])
                if len(minus) > 1 and minus[1] > 0:
                    # print("changed from minus test")
                    idline = bisect.bisect_left(fromIds, minus[0]
                        + minus[1] - 1)
                    # print("not adding to changed 2", fromuuids[fromIds[idline-1]])
            if len(plus) == 1 or plus[1] > 0:
                # we need the id for plus
                idline = bisect.bisect_left(toIds, plus[0])
                # print("plus idline", idline, 'for', plus[0])
                # print("adding to changed to", idline, toIds[idline], tolines[toIds[idline]])
                changed_ids.add(touuids[toIds[idline]])
                if len(plus) > 1 and plus[1] > 0:
                    idline = bisect.bisect_left(toIds, plus[0]+ plus[1]- 1)
                    # print("adding to changed to", touuids[toIds[idline-1]])

        ids = ", ".join(list(changed_ids))
        # ids = list(changed_ids)[0]
        # print("changed ids", ids)
        if l1 == '@':
            l = "%s%s %s" % (l1, l2, ids)
        else:
            if ndiff:
                l = "n [%s] %s" % (l1, l2)
            else:
                l = "[%s] %s" % (l1, l2)
        # sys.stdout.write("    %s\n" % (l))
        outlines.append("    %s" % (l))
    return(outlines)

def compare(fromlines, tolines):

    df = difflib.Differ()
    count = 0
    for line in df.compare(fromlines, tolines):
        l = line.rstrip()
        l1 = l[0]
        l1 = "[%s] " % l1
        l2 = l[1:]
        # sys.stdout.write("%2d    %s%s\n" % (count, l1, l2))
        # print("%2d    %s%s\n" % (count, l1, l2))
        count+=1

def get_histories(filetuple, hist={}):
    """
        Return hash of lists of lists:
        uuid:
            [timestamp change_line,
                diff line,
                diff line,
                ...],
            [timestamp change_line,
                diff line,
                diff line,
                ...],
            ...
        uuid:
            [...]
    """
    # print("\ngetting histories from:", logfile)
    logfile, relfile = filetuple
    fo = open(logfile, 'r')
    lines = [x.rstrip() for x in fo.readlines()]
    fo.close()
    current_timestamp = ''
    current_timestamp_changes = []
    current_lines = []
    current_id = ''
    for line in lines:
        # print("processing line '%s'" % line)
        m = id_regex.match(line)
        if m:
            continue
        m = timestamp_regex.match(line)
        if m:
            current_timestamp = m.group(1)
            # print('timestamp', current_timestamp)
            continue
        m = at_regex.match(line)
        if m:
            # we have an @@ line
            if len(m.groups()) == 3:
                if current_id and current_lines:
                    # bisect.insort current list in list for current_id. Since the first item in the list will be the datetime stamp and line-range, the items for current_id will be properly sorted.
                    bisect.insort(hist.setdefault(current_id, []),
                        current_lines)
                    current_lines = []
                current_lines.append("%s %s: -%s +%s" % (current_timestamp,
                     relfile, m.group(1), m.group(2)))
                current_id = m.group(3)
            else:
                # should not happen
                print("error, missing id", line)
            continue
        # line will have the leading whitespace of the log file
        current_lines.append(line)
    return(hist)

def getLogFiles(pth='/Users/dag/etm-qt/etmdata'):
    """yield the list of files in topdir and its subdirectories whose
    names match pattern."""
    pattern='[!.]*.log'
    filelist = []
    paths = [pth]
    common_prefix = os.path.commonprefix(paths)
    for d in paths:
        if d:
            for path, subdirs, names in os.walk(d, followlinks=True):
                for name in names:
                    if fnmatch.fnmatch(name, pattern):
                        full_path = os.path.join(path,name)
                        rel_path = relpath(full_path, common_prefix)
                        tup = (full_path, rel_path)
                        add2list(filelist, tup)
    return(common_prefix, filelist)

if __name__ == '__main__':
    from pprint import pprint
    if len(sys.argv) < 3:
        fromlines = [
            '* item 1',
            '@i uuid1-ed-d445-4eba-91c1-54d9bfcfce58',
            '- item 2' ,
            'line 2a',
            'line 2b',
            '@i uuid2-76-846d-48d6-9da8-02eec7cd7b5c',
            '= @c default test',
            '- item 3',
            'line 3',
            '@i uuid3-d7-ba72-4535-8cfb-c1a26dbb9bee',
            ]
        tolinesmove = [
            '= @c default test',
            '* item 1',
            '@i uuid1-ed-d445-4eba-91c1-54d9bfcfce58',
            '+ @c group test' ,
            '+ item 2',
            'line 2a',
            'line 2b',
            '@i uuid2-76-846d-48d6-9da8-02eec7cd7b5c',
            '+ item 3',
            'line 3',
            '@i uuid3-d7-ba72-4535-8cfb-c1a26dbb9bee',
            ]
        tolinesplus = [
            '= orig defaults @c default test',
            '* item 1',
            '@i  1',
            '+ item 2a',
            'line 2a',
            '@i  2a',
            '+ item 2',
            'line 2',
            '@i  2',
            '- item 3',
            'line 3',
            'Id 3',
            ]
        tolinesminus = [
            '* item 1',
            '@i  1',
            '+ item 2',
            '@i  2',
            '- item 3',
            'line 3',
            'Id 3',
            ]
        tolines = tolinesmove

        orig = [
            '1',
            '= @c meetings',
            '3',
            '+ 4',
            '+ 5',
            '+ 6',
            '7',
            '* Sales meeting @s 11a Mon @l Conference Room',
            '@i uuid3-d7-ba72-4535-8cfb-c1a26dbb9bee',
            ]
        new = [
            '= @c meetings',
            '2',
            '3',
            '+ 4',
            '+ 6',
            '+ 5',
            '7',
            '* Sales meeting @s 11:00a Fri @l Conference Room',
            '@i uuid3-d7-ba72-4535-8cfb-c1a26dbb9bee',
            ]

        # diff(fromlines, tolines, True)
        outlines = diff(fromlines, tolines)
        for line in outlines:
            print(line)
        common, flist = getLogFiles()
        hist = {}
        for f in flist:
            # print("processing", f[0])
            hist = get_histories(f, hist)
        for key,value in hist.items():
            print(key)
            for lst in value:
                for line in lst:
                    print("    %s" % line)
    else:
        fromfile, tofile = sys.argv[1:3]
        # print(fromfile, tofile)
        # filediff(fromfile, tofile, True)
        difflines = filediff(fromfile, tofile)
        for line in difflines:
            print(line)
