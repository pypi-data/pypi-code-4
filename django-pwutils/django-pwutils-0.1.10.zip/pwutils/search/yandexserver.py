import logging
import urllib
import urllib2
import lxml.etree

from django.conf import settings

from base import BaseSearchEngine

logger = logging.getLogger(__name__)


YANDEXSERVER_URL = getattr(settings, 'YANDEXSERVER_URL', 'http://yandex.ru/')


class YandexServer(BaseSearchEngine):

    def get_results(self, query):
        params = {'text': query.encode('utf8'),
                  'xml': '1',
                  'numdoc': 1000
                 }
        response = urllib2.urlopen(YANDEXSERVER_URL + '?' + urllib.urlencode(params))

        root = lxml.etree.fromstring(response.read())

        response = root.find('response')
        results = response.find('results')
        matches = self.find_results_with_grouping(results)
        count = response.find('found[@priority="all"]')
        return {'matches': matches,
                'count': count and count.text() or 0
               }

    def make_hl(self, text):
        hl = text.replace('<hlword priority="strict">', '<b>')\
                 .replace('</hlword>', '</b>')\
                 .replace('<passage>', '')\
                 .replace('</passage>', '')\
                 .replace('<properties>', '<div style="display:none">')\
                 .replace('</properties>', '</div>')
        return hl

    def make_title(self, text):
        title = text.replace('<hlword priority="strict">', '<b>')\
                 .replace('</hlword>', '</b>')\
                 .replace('<title>', '')\
                 .replace('</title>', '')
        return title

    def find_results_with_grouping(self, results):
        matches = []
        if not results:
            return matches

        for group in results.findall('grouping/group'):
            doc = group.find('doc')

            highlights = list()
            for p in doc.findall('passages/passage'):
                hl_text = lxml.etree.tostring(p,
                                          encoding='utf8',
                                          method='html')
                highlights.append(self.make_hl(hl_text))

            title = lxml.etree.tostring(doc.find('title'),
                                        encoding='utf8',
                                        method='html')
            title = self.make_title(title)

            matches.append({'url': doc.find('url').text,
                            'highlight': '<br/>'.join(highlights),
                            'title': title,
                           })

        return matches
