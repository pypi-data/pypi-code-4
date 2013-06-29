import datetime
import hashlib
import feedparser

from django.conf import settings
from django.utils.encoding import smart_str

from player.crawler.models import CrawlerCollection
from player.crawler.backends.utils import collect_items_extracted, create_extraction_report
from player.data.models import Collection, Item


def get_collection_link(crawler_collection):
    """
    This function will return a representative link to collection configured with
    the scrap tool.
    """
    return crawler_collection.collection_code


def get_collection_schema(collection_code):
    """
    This function will return the collection schema configured in your scrap tool
    with collection_code
    """
    feed = feedparser.parse(collection_code)
    first_item = feed.entries[0]
    schema = {}
    for field_name in first_item.keys():
        schema[field_name] = {u'id': field_name,
                              u'type': 'text',
                              u'is_match_up': False}
    # some replacements because RSS specs
    schema['link'].update({'type': 'url', 'is_match_up': True})
    if 'content' in schema:
        schema['content'].update({'type': 'html'})
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
    # TODO: to implement
    return True


def extract_collection_data(crawler_collection):
    """
    This function will parse the collection as configured in your scrap tool.
    """
    collection_code = crawler_collection.collection_code
    collections_to_extract = Collection.objects.filter(crawler_collection__collection_code=collection_code)
    items_dict = {'added': [], 'updated': [], 'deleted': []}
    for collection in collections_to_extract:
        items_extracted = []
        has_matchup_fields = collection.fields.is_mapped().filter(is_matchup=True).exists()
        feed = feedparser.parse(collection_code)
        for entry in feed.entries:
            uid = hashlib.md5()
            field_dict = {}
            for field in collection.fields.all().is_mapped():
                field_name = field.mapped_field
                value = entry[field_name]
                if field.is_matchup or not has_matchup_fields:
                    uid.update(smart_str(value))
                field_dict[field.slug] = value
                item = Item(uid=uid.hexdigest(), collection=collection)
                item.content = field_dict
                items_extracted.append(item)
        success, log, added_items, updated_items, deleted_items_uid, deleted_items = collect_items_extracted(items_extracted, collection)
        collection.last_crawling_time = datetime.datetime.now()
        collection.save()
        items_dict['added'] += added_items
        items_dict['updated'] += updated_items
        items_dict['deleted'] += deleted_items
        crawler_collection.last_crawling_time = datetime.datetime.now()
        crawler_collection.last_job_time = datetime.datetime.now()
        crawler_collection.save()
        affected_collections = Collection.objects.filter(crawler_collection=crawler_collection)

        create_extraction_report(success, crawler_collection, items_dict, log)


def get_collection_codes(login, password=None):
    """ returns None because code is edited by hand"""
    return None


# ----- testing functions (used in unit tests) -----


def create_test_crawler_collection():
    """ Create test collection """
    return CrawlerCollection.objects.create(
            collection_code=settings.CRAWLER_TEST_COLLECTION_CODE,
    )


def run_test_extraction_process():
    """ Run extraction of test data in scraping tool """
    raise NotImplementedError()
