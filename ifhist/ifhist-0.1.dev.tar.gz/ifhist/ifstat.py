#!/usr/bin/env python

import time
import argparse
import collections

from . import docSplit, version, usage

class IfStat(object):
    """
    """
    statsFile = "/proc/net/dev"
    mb = 1048576

    def __init__(self, device):
        """
        Initialise the class.

        @arg device: Name of a network interface.
        @type device: str
        """
        self.log = open("/var/local/%s.ifstats" % device, "a+")
        self.history = map(lambda x: map(lambda y: int(y), x.strip().split()),
            self.log)
        self.counts = collections.OrderedDict([
            ("now", [0, 0, 0, "this session"]),
            ("day", [86400, 0, 0, "last day"]),
            ("week", [604800, 0, 0, "last week"]),
            ("month", [2592000, 0, 0, "last month"])
        ])

        for i in open(self.statsFile).readlines()[2:]:
            data = i.split()

            if data[0] == "%s:" % device:
                for j in self.counts:
                    self.counts[j][1] += int(data[1])
                    self.counts[j][2] += int(data[9])
                #for
                break
            #if
        #for
    #__init__

    def __str__(self):
        """
        """
        now = time.time()

        for line in self.history:
            for i in self.counts:
                if line[0] > now - self.counts[i][0]:
                    self.counts[i][1] += line[1]
                    self.counts[i][2] += line[2]
                #if

        return '\n'.join(map(lambda x: "%s : RX: %i (%iM), TX: %i (%iM)" % (
            self.counts[x][3], self.counts[x][1], self.counts[x][1] / self.mb,
            self.counts[x][2], self.counts[x][2] / self.mb), self.counts))
    #__str__

    def store(self):
        """
        Store statistics in the log.
        """
        self.log.write("%i %i %i\n" % (time.time(), self.counts["now"][1],
            self.counts["now"][2]))
    #store
#IfStat

def main():
    """
    Main entry point.
    """
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=usage[0], epilog=usage[1])
    parser.add_argument("-s", dest="store", default=False, action="store_true",
        help="store statistics")
    parser.add_argument('-v', action="version", version=version(parser.prog))
    parser.add_argument("DEV", type=str, help="network interface")

    args = parser.parse_args()

    S = IfStat(args.DEV)
    if args.store:
        S.store()
    else:
        print S
#main

if __name__ == '__main__':
    main()
