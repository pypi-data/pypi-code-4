#!/usr/bin/env python

from re import match, search
from os import system

class Submodule:
    name = None
    path = None
    url = None

    def is_valid(self):
        #print "name: %s\npath: %s\nurl: %s\n" % (self.name, self.path, self.url)
        if self.name and self.path and self.url:
            return True
        return False

    def add(self):
        system( "git submodule add --name %s %s %s" % (self.name, self.url, self.path) )

    def __init__(self, name, path=None, url=None):
        self.name = name
        self.path = path
        self.url = url

    def __unicode__(self):
        return self.name


def main():
    with open('.gitmodules', 'r') as f:
        submodule = None
        submodules = []

        for line in f.readlines():
            m = match(r"^\[submodule \"(?P<name>[^\0^\"]+)\"\]$", line)
            if m:
                if submodule and submodule.is_valid():
                    submodules.append(submodule)

                submodule = Submodule(m.group('name'))
            else:
                m = match(r"^\s*(?P<key>\w+)\s*=\s(?P<value>[^\0^\"]+)$", line)
                if m and submodule:
                    key = m.group('key')
                    value = m.group('value')
                    if key == 'path':
                        submodule.path = value.strip()
                    elif key == 'url':
                        submodule.url = value.strip()
        if submodule.is_valid():
            submodules.append(submodule)

    for submodule in submodules:
        submodule.add()


if __name__ == '__main__':
    main()