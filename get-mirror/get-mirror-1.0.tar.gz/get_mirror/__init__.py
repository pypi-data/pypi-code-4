import os
import sys
import json
import urllib
from optparse import make_option, OptionParser
from pdb import set_trace as bp

class GetMirror(object):
    def __init__(self, server):
         info = urllib.urlopen("http://api.ipinfodb.com/v3/ip-city/?key=153a"\
                 "18f73f6aa792096592198d88b470cdd575c14b089174"\
                 "c9d5127075bfef1e&format=json").read()
         info = json.loads(info)
         self.country = info['countryCode'].lower()
         self.server = server

    def fetch(self):
        mirrors = urllib.urlopen("https://raw.github.com/imcj/get-mirror/"\
                                 "master/mirrors/%s.json" % self.server)\
                        .read()
        return json.loads(mirrors)

    def list(self):
        pass

    def get(self):
        if "ubuntu" == self.server:
            sys.stdout.write("%s.archive.ubuntu.com" % self.country)
            return

        mirrors = self.fetch()
        mirror = mirrors.get(self.country, None)
        if not mirror:
            mirror = mirrors.get("default", "")

        sys.stdout.write(mirror[0])
def __main__():
    usage = "usage: get-mirror [options] arg1"
    option_list = [
        make_option("-l", "--list", action="store_true", dest="list"),
    ]
    parser = OptionParser(usage=usage, option_list=option_list)
    (opts, args) = parser.parse_args()

    if 0 == len(args):
        parser.print_help()
        return

    m = GetMirror(args[0])
    if opts.list:
        m.list()
    else:
        m.get()

if __name__ == "__main__":
    __main__()
