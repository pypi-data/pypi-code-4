#!/usr/bin/env python

import argparse, logging, nagiosplugin, os

class FilecountMetric(nagiosplugin.Resource):
    
    def __init__(self, path, recurse, strict):
        self.path = path
        self.recurse = recurse
        self.strict = strict
        
    def probe(self):
        fcnt = 0
        tree = os.walk(self.path)
        for r, d, f in tree:
                if self.strict:
                    fcnt += len(f)
                else:
                    fcnt += len(d) + len(f)
                if self.recurse == False:
                    break
        return [nagiosplugin.Metric('filecountmetric', fcnt, '')]
        

@nagiosplugin.guarded
def main():
    
    argp = argparse.ArgumentParser(description='Nagios plugin to check filecounts')
    
    argp.add_argument('-p', '--path', required=True,
                      help='directory to check')
    argp.add_argument('-r', '--recurse', action='store_true',
                      help='recurse directory')
    argp.add_argument('-s', '--strict', action='store_true',
                      help='consider files only, not dirs')
    argp.add_argument('-w', '--warning', metavar='RANGE', default=0,
                      help='warning if filecount threshold is outside RANGE')
    argp.add_argument('-c', '--critical', metavar='RANGE', default=0,
                      help='critical if filecount threshold is outside RANGE')
    argp.add_argument('-v', '--verbose', action='count', default=0,
                      help='increase verbosity (use up to 3 times)')
    
    args=argp.parse_args()
    
    check = nagiosplugin.Check(
            FilecountMetric(args.path, args.recurse, args.strict),
            nagiosplugin.ScalarContext('filecountmetric', args.warning, args.critical))
    check.main(verbose=args.verbose)

if __name__ == "__main__":
    main()