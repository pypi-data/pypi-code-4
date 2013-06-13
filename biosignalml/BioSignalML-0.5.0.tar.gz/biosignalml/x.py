from transports import WebStreamReader


if __name__ == '__main__':
#=========================

  import sys
  import logging

  logging.getLogger().setLevel(logging.DEBUG)

  if len(sys.argv) < 5:
    print 'Usage: %s endpoint uri start duration' % sys.argv[0]
    sys.exit(1)

  for d in WebStreamReader(sys.argv[1], sys.argv[2], start=float(sys.argv[3]),
                                                     duration=float(sys.argv[4]) ):
    print d


