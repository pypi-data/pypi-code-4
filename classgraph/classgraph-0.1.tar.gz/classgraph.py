#!/usr/bin/env python
import fileinput
import re

newclassdef = re.compile(r"class +([\w]+):")
classdef = re.compile(r"class +([\w]+)\(([\w\.]+)\):")


def process(line):
    if line.startswith("class "):
        ncm = newclassdef.match(line)
        if ncm:
            print "%s;" % ncm.group(1)
        cm = classdef.match(line)
        if cm:
            print "%s -> %s;" % (cm.group(1), cm.group(2).replace(".", "_"))

if __name__ == "__main__":
    print "digraph G\n{"
    for line in fileinput.input():
        process(line)
    print "}"
