# encoding: utf-8
import urllib2
from xml.etree import ElementTree
from xml.etree.ElementTree import Element
from urllib import urlencode


class DoiFinder(object):

    def __init__(self, format='unixref', user=None, passwd=None):

        self._user = user
        self._passwd = passwd

        allowed_formats = ['unixref', 'unixsd', 'xsd_xml']
        if format in allowed_formats:
            self._format = format
        else:
            raise ValueError('format %s not allowed' % format)

    def _extract_doi_from_xml(self, xml):
        try:
            if self._format == 'unixref':
                doi = ElementTree.fromstring(xml).find(".//doi_data/doi").text
            elif self._format == 'unixsd':
                doi = ElementTree.fromstring(xml).find(".//{http://www.crossref.org/qrschema/3.0}doi").text
            elif self._format == 'xsd_xml':
                doi = ElementTree.fromstring(xml).find(".//{http://www.crossref.org/qrschema/2.0}doi").text
        except AttributeError:
            doi = None

        return doi

    def _get_query_batch_xml(self, **kwargs):

        ET = ElementTree

        attrib = {'version': '2.0',
                  'xmlns': 'http://www.crossref.org/qschema/2.0',
                  'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
                  'xsi:schemaLocation': 'http://www.crossref.org/qschema/2.0 file:/Users/fabiobatalha/Trabalho/tmp/crossref/crossref_query_input2.0.xsd'}

        equery_batch = Element('query_batch', attrib=attrib)

        ehead = Element('head')
        eemail_address = Element('email_address')
        eemail_address.text = kwargs['email_address']
        edoi_batch_id = Element('doi_batch_id')
        edoi_batch_id.text = kwargs['doi_batch_id']
        ebody = Element('body')
        equery = Element('query', attrib={'enable-multiple-hits': 'false',
                                          'forward-match': 'false',
                                          'key': kwargs['key']})

        eissn = Element('issn', match='optional')
        eissn.text = kwargs['issn']

        ejournal_title = Element('journal_title', match='optional')
        ejournal_title.text = kwargs['journal_title']

        earticle_title = Element('article_title', match='fuzzy')
        earticle_title.text = kwargs['article_title']

        eauthor = Element('author', match='optional')
        eauthor.text = kwargs['author']

        eyear = Element('year', match='optional')
        eyear.text = kwargs['year']

        evolume = Element('volume', match='optional')
        evolume.text = kwargs['volume']

        eissue = Element('issue')
        eissue.text = kwargs['issue']

        efirst_page = Element('first_page', match='optional')
        efirst_page.text = kwargs['first_page']

        equery_batch.append(ehead)
        equery_batch.append(ebody)
        ehead.append(eemail_address)
        ehead.append(edoi_batch_id)
        ebody.append(equery)

        if kwargs['issn']:
            equery.append(eissn)

        if kwargs['author']:
            equery.append(eauthor)

        if kwargs['volume']:
            equery.append(evolume)

        if kwargs['issue']:
            equery.append(eissue)

        if kwargs['first_page']:
            equery.append(efirst_page)

        if kwargs['year']:
            equery.append(eyear)

        if kwargs['article_title']:
            equery.append(earticle_title)

        query_xml = ET.tostring(equery_batch, encoding='utf-8', method='xml')

        return query_xml

    def _query_to_crossref(self, query_xml):

        data = {'usr': self._user,
                'pwd': self._passwd,
                'format': self._format,
                'qdata': '<?xml version = "1.0" encoding="utf-8"?>%s' % query_xml}

        req = urllib2.Request("http://doi.crossref.org/servlet/query", urlencode(data))

        return urllib2.urlopen(req).read()

    def find_doi(self,
                 key='any',
                 email_address="crossref@crossref.org",
                 doi_batch_id="crossref",
                 issn=None,
                 journal_title=None,
                 article_title=None,
                 author=None,
                 year=None,
                 volume=None,
                 issue=None,
                 first_page=None):

        meta = {'key': key,
                'email_address': email_address,
                'doi_batch_id': doi_batch_id,
                'issn': issn,
                'journal_title': journal_title,
                'article_title': article_title,
                'author': author,
                'year': year,
                'volume': volume,
                'issue': issue,
                'first_page': first_page}

        query_xml = self._get_query_batch_xml(**meta)
        response = self._query_to_crossref(query_xml)
        doi = self._extract_doi_from_xml(response)

        return doi
