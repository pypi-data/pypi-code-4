import re
import calendar
import urlparse
import gzip
from collections import Counter
from cStringIO import StringIO

from dateutil import parser as date_parser

from bs4 import BeautifulSoup

from twisted.python import log
from twisted.internet import defer, reactor, task
from twisted.web import client

from csat.graphml.builder import GraphMLDocument, Attribute
from csat.tasks import Task


class PipermailCollector(object):

    date_regex = re.compile(r'({})\s(\d{{4}})'.format(
        '|'.join(calendar.month_name).strip('|')))

    split_regex = re.compile(r'From \S+ at \S+\s+\S+\s+\S+\s+\d\d?\s+(?:\d\d:)'
                             '{2}\d\d \d{4}')

    from_regex = re.compile(r'(\S+) at (\S+) \([^\)]+\)')

    def __init__(self, task_manager, logger, base_url, concurrency):
        self.tasks = task_manager
        self.log = logger
        self.url = base_url
        self.getPageQueue = defer.DeferredSemaphore(concurrency)

    def run(self):
        self.fetchTask = self.tasks.new('Fetching data')
        self.parseTask = self.tasks.new('Parsing emails')
        self.publishTask = self.tasks.new('Creating graph')

        self.setup_twisted_logging()

        self._init_graph()

        def write_graphml(stream):
            return self.graph.to_file(stream)

        self.graph.write_graphml = self.graph.to_file

        def stop(_):
            reactor.stop()

        def catchError(failure):
            self.error = failure

        def collect():
            d = self.asyncCollect(reactor)
            d.addErrback(catchError)
            d.addCallback(stop)

        self.error = None
        reactor.callWhenRunning(collect)
        reactor.run()

        if self.error:
            self.error.raiseException()

        return self.graph

    def _init_graph(self):
        self.graph = GraphMLDocument()

        self.graph.attr(Attribute.GRAPH, 'merge_key')

        self.graph.attr(Attribute.NODE, 'domain')

        self.graph.attr(Attribute.NODE, 'email')
        self.graph.attr(Attribute.NODE, 'mails_sent', 'int')

        self.graph.attr(Attribute.EDGE, 'count', 'int')
        self.graph.attr(Attribute.ALL, 'type')

        self.subgraph = self.graph.digraph(None, {
            'merge_key': 'domain'
        }).node(None, {
            'domain': 'people'
        }).subgraph(None, {
            'merge_key': 'email'
        })

    def setup_twisted_logging(self):
        observer = log.PythonLoggingObserver()
        observer.start()
        log.defaultObserver.stop()

        client.HTTPClientFactory.noisy = False

    @defer.inlineCallbacks
    def asyncCollect(self, reactor):
        # Result is a list of results with an entry for each month
        self.fetchTask.statusText = 'Retrieving data from {}...'.format(
            self.url)
        result = yield self.getSoup(self.url).addCallback(self.gotIndex)
        self.fetchTask.setCompleted()

        senders = {}
        threads = {}

        self.parseTask.steps = len(result)

        for success, mails in result:
            if success:
                first = True
                for mail in mails:
                    if first:
                        date = mail['headers']['date']
                        text = 'Parsing email data for {}...'.format(
                            date.strftime('%Y-%m'))
                        self.parseTask.statusText = text
                        first = False
                    sender_id = mail['headers']['from']
                    subject_id = mail['headers']['subject']
                    senders.setdefault(sender_id, []).append(mail)
                    threads.setdefault(subject_id, []).append(mail)
            self.parseTask.makeStep()
        self.parseTask.setCompleted()

        self.publishTask.status = Task.RUNNING
        self.publishTask.statusText = 'Building graph...'
        self.publishTask.steps = len(senders) + len(threads)

        yield task.coiterate(self.publishSenders(threads, senders))

    def publishSenders(self, threads, senders):
        senders_map = {}

        self.publishTask.statusText = 'Publishing nodes info...'
        for sender, mails in senders.iteritems():
            sender_id = len(senders_map)
            senders_map[sender] = self.subgraph.node(sender_id, {
                'type': 'person',
                'email': sender,
                'mails_sent': len(mails)
            })
            self.publishTask.makeStep()
            yield None

        self.publishTask.statusText = 'Defining edge weights...'
        interactions = Counter()
        for subject, mails in threads.iteritems():
            def key(m):
                return m['headers']['date']
            mails = sorted(mails, key=key)
            sorted_posters = (m['headers']['from'] for m in mails[1:])
            op = mails[0]['headers']['from']
            replies = ((p, op) for p in sorted_posters if p != op)
            for reply in replies:
                interactions[reply] += 1
            self.publishTask.makeStep()
            yield None

        self.publishTask.statusText = 'Publishing edges info...'
        self.publishTask.steps += len(interactions)
        for (src, dst), count in interactions.iteritems():
            src, dst = senders_map[src], senders_map[dst]
            self.subgraph.edge(src, dst, {
                'type': 'interaction',
                'count': count,
            })
            yield None

        self.publishTask.setCompleted()

    def getPage(self, url):
        url = str(url)
        return self.getPageQueue.run(client.getPage, url)

    def getSoup(self, url):
        return self.getPage(url).addCallback(BeautifulSoup)

    def getGzipCompressed(self, url):
        def decompress(payload):
            stream = StringIO(payload)
            try:
                return gzip.GzipFile(fileobj=stream).read()
            except IOError:
                self.log.warning('{} is not a gzipped resource.'.format(url))
                return payload
        return self.getPage(url).addCallback(decompress)

    def gotIndex(self, page):
        deferreds = []
        rows = page.find_all('tr')
        self.fetchTask.steps = len(rows)
        for row in rows:
            cells = row.find_all('td')
            header = cells[0].get_text()
            date = self.date_regex.match(header)
            if not date:
                continue
            month, year = date.groups()
            month, year = list(calendar.month_name).index(month), int(year)

            archive = cells[-1].a.get('href')
            archive = urlparse.urljoin(self.url, archive)

            d = self.getGzipCompressed(archive)

            def inc(r):
                self.fetchTask.makeStep()
                return r
            d.addCallback(inc)
            d.addCallback(self.gotMonth, year, month)
            deferreds.append(d)
        return defer.DeferredList(deferreds)

    def gotMonth(self, page, year, month):
        for m in self.split_regex.split(page)[1:]:
            try:
                mail = self.parseMail(m)
            except:
                self.log.error('Could not parse mail in archive of month '
                               '{}-{:02d}'.format(year, month))
            else:
                yield mail

    def parseMail(self, text):
        mail = text.strip().split('\n\n', 1)

        headers = mail[0]
        body = mail[1] if len(mail) == 2 else ''

        headers = re.split('\n(?!\s)', headers)
        headers = [re.sub(r'\s+', ' ', h) for h in headers]
        headers = [self.parseHeader(h) for h in headers]

        parts = body.split('\n-------------- next part --------------\n')

        return {
            'headers': dict(headers),
            'body': parts,
        }

    def parseHeader(self, header):
        key, value = header.split(': ', 1)

        func = 'parseHeader_{}'.format(key.upper())
        func = getattr(self, func, None)
        if callable(func):
            value = func(value)

        return (key.lower(), value)

    def parseHeader_FROM(self, val):
        match = self.from_regex.match(val)
        email = '@'.join(match.groups())
        return email

    def parseHeader_DATE(self, val):
        try:
            return date_parser.parse(val)
        except ValueError:
            # Try again using fuzzy parsing
            try:
                parsed = date_parser.parse(val, fuzzy=True)
                self.log.info('Fuzzy parsing for date: \'{}\'\n'
                              '        Resulting date: \'{:%a, %d %b %Y '
                              '%H:%M:%S %z}\''.format(val, parsed))
                return parsed
            except ValueError:
                self.log.warning('Could not parse date: \'{}\''.format(val))
                raise

    def parseHeader_REFERENCES(self, val):
        return val.split(' ')

    def parseHeader_SUBJECT(self, val):
        return re.sub(r'^([a-zA-Z]{1,3}:\s+)+', '', val)
