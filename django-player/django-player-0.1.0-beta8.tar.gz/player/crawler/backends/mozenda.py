import datetime
import httplib2
import hashlib
import time

from lxml import etree

from django.conf import settings
from django.utils.encoding import smart_str

from player.crawler.models import CrawlerCollection, Report
from player.crawler.exceptions import CrawlerHttpException
from player.crawler.backends.utils import collect_items_extracted, create_extraction_report
from player.data.models import Collection, Item


def get_collection_link(crawler_collection):
    """
    This function will return a representative link to collection configured with
    the scrap tool.
    """
    return 'http://www.mozenda.com/console/#collections/%s/' % crawler_collection.collection_code


def get_collection_schema(collection_code):
    """
    This function will return the collection schema configured in your scrap tool
    with collection_code
    """
    params = [('Operation', 'Collection.GetFields'),
              ('CollectionID', collection_code)]
    response = _mozenda_request(params)

    if response[0]['status'] == '200':
        parser = etree.fromstring(response[1])
        fields = parser.findall('FieldList/Field')
        schema = {}
        for field in fields:
            field_name = field.find('Name').text
            field_id = field.find('FieldID').text
            field_is_system = field.find('IsSystem').text
            field_is_match_up = field.find('IsMatchUp').text
            schema[field_name] = {u'id': field_id,
                                  u'type': 'text',
                                  u'is_system': field_is_system,
                                  u'is_match_up': field_is_match_up}
        return schema


def load_collection_schema(crawler_collection):
    """
    This function will load the collection schema configured in your scrap tool
    with collection_code
    """
    schema = get_collection_schema(crawler_collection.collection_code)
    if schema:
        crawler_collection.schema = schema
        crawler_collection.save()


def has_new_data(crawler_collection):
    """ return True if scraping tool have new data to extract """
    collection_code = crawler_collection.collection_code
    last_job_time = crawler_collection.last_job_time
    if last_job_time is None:
        return True  # crawler never has extracted any data from mozenda
    mozenda_last_job_time = _get_last_job_time(collection_code)
    if mozenda_last_job_time is None:
        return False  # Mozenda never has launch any extraction Job
    if mozenda_last_job_time > last_job_time:
        return True  # Mozenda Job is newer than our data
    return False  # Mozenda Job is older


def extract_collection_data(crawler_collection):
    """
    This function will parse the collection as configured in your scrap tool.
    """
    collection_code = crawler_collection.collection_code
    # - Get view_id
    params = [('Operation', 'Collection.GetViews'),
              ('CollectionID', collection_code)]

    response = _mozenda_request(params)
    if response[0]['status'] == '200':
        parser = etree.fromstring(response[1])
        view_id = parser.find('ViewList/View/ViewID').text
    collections_to_extract = Collection.objects.filter(crawler_collection__collection_code=collection_code)

    params = [('Operation', 'View.GetItems'),
              ('ViewID', view_id)]

    response = _mozenda_request(params)
    if response[0]['status'] == '200':
        parser = etree.fromstring(response[1])
        nodes = parser.findall('ItemList/Item')
        items_dict = {'added': [], 'updated': [], 'deleted': []}
        for collection in collections_to_extract:
            items_extracted = []
            has_matchup_fields = collection.fields.is_mapped().filter(is_matchup=True).exists()
            for node in nodes:
                uid = hashlib.md5()
                field_dict = {}
                for field in collection.fields.all().is_mapped():
                    field_name = field.mapped_field
                    xml_field_name = field_name.replace(' ', '')
                    value = node.find(xml_field_name).text
                    if field.is_matchup or not has_matchup_fields:
                        uid.update(smart_str(value))
                    field_dict[field.slug] = value
                item = Item(uid=uid.hexdigest(), collection=collection)
                item.content = field_dict
                items_extracted.append(item)
                # note: the items are not save yet in database (only in memory)
                # when we confirm we passed the security thresholds, we will save them

            success, log, added_items, updated_items, deleted_items_uid, deleted_items = collect_items_extracted(items_extracted, collection)
            collection.last_crawling_time = datetime.datetime.now()
            collection.save()
            items_dict['added'] += added_items
            items_dict['updated'] += updated_items
            items_dict['deleted'] += deleted_items
        crawler_collection.last_crawling_time = datetime.datetime.now()
        crawler_collection.last_job_time = _get_last_job_time(collection_code)
        crawler_collection.save()
        affected_collections = Collection.objects.filter(crawler_collection=crawler_collection)

        create_extraction_report(success, crawler_collection, items_dict, log, response[1])
    else:  # if response status code is not 200
        report = Report(
            crawler_collection=crawler_collection,
            crawling_time=datetime.datetime.now(),
        )
        report.return_code = 'err'
        report.traceback = str(response)
        report.crawled_data = ''
        report.save()


def get_collection_codes(login, password=None):
    """returns a list of tuples (code, label)

    username is actually the API key for Mozenda. It's called
    username to keep persistence between Mozenda and Dapper backend"""

    params = [('Operation', 'Collection.GetList')]
    response = _mozenda_request(params)

    if response[0]['status'] == '200':
        parser = etree.fromstring(response[1])
        cols_ids = parser.findall('CollectionList/Collection/CollectionID')
        cols_names = parser.findall('CollectionList/Collection/Name')

        collections = []
        for i in range(len(cols_ids)):
            aux_collection = (cols_ids[i].text, cols_names[i].text)
            collections.append(aux_collection)

        return collections
    # TODO: if the response code is not good, raise an exception


# ----- testing functions (used in unit tests) -----


def create_test_crawler_collection():
    """ Create test collection """
    return CrawlerCollection.objects.create(
            collection_code=settings.CRAWLER_TEST_COLLECTION_CODE,
    )


def run_test_extraction_process():
    """ Run extraction of test data in scraping tool """
    params = [('Operation', 'Agent.Run'),
              ('AgentID', settings.CRAWLER_TEST_AGENT_ID)]
    response = _mozenda_request(params)
    if response[0]['status'] == '200':
        parser = etree.fromstring(response[1])
        job_id = parser.findall('JobID')[0].text
        job_status = 'Running'
        job_status_params = [('Operation', 'Job.Get'),
                             ('JobID', job_id)]
        while job_status != 'Done':
            job_status_response = _mozenda_request(job_status_params)
            if job_status_response[0]['status'] == '200':
                job_status_parser = etree.fromstring(job_status_response[1])
                job_status = job_status_parser.findall('Job/Status')[0].text
                time.sleep(2)


# ----- auxiliar functions -----


def _get_last_job_time(collection_code):
    params = [('Operation', 'Agent.GetJobs'),
              ('AgentID', collection_code)]
    response = _mozenda_request(params)
    if response[0]['status'] == '200':
        parser = etree.fromstring(response[1])
        for job_status in parser.findall('JobList/Job'):
            if job_status.find('Status').text == 'Done':
                end_date_str = job_status.find('Ended').text
                return datetime.datetime.strptime(end_date_str, r'%Y-%m-%d %H:%M:%S')
    return None


def _build_url_query(api_key, params=[]):
    """build the url query string to perform a query to mozenda"""
    ops = ''
    for i in params:
        ops += '&%s=%s' % (i[0], i[1])

    url = '%s?WebServiceKey=%s&Service=Mozenda10%s'
    return url % (settings.CRAWLER_HOST, api_key, ops)


def _mozenda_request(params):
    http = httplib2.Http()

    response = http.request(_build_url_query(settings.CRAWLER_LOGIN, params))
    if response[0]['status'] == '200':
        return response
    else:
        raise CrawlerHttpException(response[0]['status'],
                                   response[1])


def _get_collection_id_from_code(collection_code):
    """returns the collection id from the collection code"""
    collections = get_collection_codes(settings.CRAWLER_LOGIN)

    for col in collections:
        if col[1] == collection_code:
            return col[0]

    return ''  # TODO: probably is a better idea to raise an exception
