import argparse
import logbook
import requests
from requests.exceptions import RequestException
import time


def main():
    log = logbook.Logger('webmonitor')

    parser = argparse.ArgumentParser()
    parser.add_argument('url')
    parser.add_argument('-d', '--debug', action='store_const',
                        const=logbook.DEBUG, dest='loglevel',
                        help='Show really verbose output.')
    parser.add_argument('-v', '--verbose', action='store_const',
                        const=logbook.INFO, dest='loglevel',
                        help='Show verbose output.')
    parser.add_argument('-i', '--interval', default=30, type=float,
                        help='How many seconds to wait between checks.')
    parser.add_argument('-V', '--no-verify', default=True, dest='verify',
                        action='store_false',
                        help='Disable certificate verification on HTTPS'
                             'requests.')
    parser.set_defaults(loglevel=logbook.ERROR)
    args = parser.parse_args()

    logbook.handlers.NullHandler().push_application()
    logbook.handlers.StderrHandler(level=args.loglevel).push_application()

    last_known_good = None
    log.info('Starting monitor on %s.' % args.url)

    while True:
        log.debug('Retrieving %r' % args.url)

        try:
            r = requests.get(args.url, verify=args.verify)
            r.raise_for_status()
        except RequestException as e:
            if not last_known_good:
                last = 'Website was never up before.'
            else:
                last = 'Last recorded good response was %.2f seconds ago.' % (
                    time.time() - last_known_good
                )
            log.error('Failed to retrieve %r: %r. %s' % (args.url, e, last))
        else:
            log.info('%r is up.' % args.url)
            last_known_good = time.time()

        log.debug('Sleeping for %s seconds.' % args.interval)
        time.sleep(args.interval)
