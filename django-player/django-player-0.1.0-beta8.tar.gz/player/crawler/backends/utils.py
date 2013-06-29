import re
import sys
from copy import deepcopy
from cStringIO import StringIO

from django.db import IntegrityError
from django.utils.encoding import smart_str, smart_unicode

from player.crawler.models import Report
from player.data.models import Item


def collect_items_extracted(items_list, collection):
    """returns a boolean value that is True if the extraction is
    correct, and False in other case"""

    # first, checks if it's the first crawling (no items on the collection)
    success = False
    log = StringIO()
    added_items = []
    updated_items = []
    deleted_items_uid = []
    deleted_items = []
    if collection.item_set.count() == 0:  # first crawl, store all items
        uid_list = []
        indexes_to_remove = []
        for i, item in enumerate(items_list):
            if item.uid not in uid_list:
                item.save()
                uid_list.append(item.uid)
            else:
                indexes_to_remove.append(i)
        removed_items = 0
        for i in indexes_to_remove:
            # we remove in a second step in order to mantain the loop iteration's
            del items_list[i - removed_items]
            removed_items += 1
        success = True
        print >> log, u'First crawling'
        added_items = items_list
    else:  # some elements are not
        # get how many items are new, updated and deleted from the "old" items
        dict_new_items = {}
        for item in items_list:
            dict_new_items[item.uid] = item
        previous_items_uid = []
        new_items_uid = []

        # it needs separates the UIDs and make the checks about it
        # because on the extracted Items, the __unicode__ function
        # does not work for us, because uses the id value, and it's
        # not enough to identify a single item.
        for item in Item.objects.all().filter(collection=collection):  # valids
            previous_items_uid.append(item.uid)

        for item in items_list:
            new_items_uid.append(item.uid)

        previous_items_uid_set = set(previous_items_uid)
        new_items_uid_set = set(new_items_uid)
        created_items_uid = list(new_items_uid_set.difference(previous_items_uid_set))
        deleted_items_uid = collection.crawler_collection.check_deleted and list(previous_items_uid_set.difference(new_items_uid_set)) or []

        for deleted_item_uid in deleted_items_uid:
            try:
                item = Item.objects.get(collection=collection, uid=deleted_item_uid,
                                        is_deleted=False, is_valid=True)
                deleted_items.append({'uid': deleted_item_uid,
                                      'repr': unicode(item),
                                      'collection': unicode(item.collection)})
            except Item.DoesNotExist:  # if the item does not exists, don't mind
                pass
        updated_items_uid = list(new_items_uid_set.intersection(previous_items_uid_set))

        aux = [uid for uid in updated_items_uid]
        for uid in aux:
            new_content = dict_new_items[uid].content
            if not Item.objects.get(collection=collection, uid=uid,
                                    is_deleted=False,
                                    is_valid=True).has_changed(new_content):
                updated_items_uid.remove(uid)

        # for now only checks as numeric values
        new_elements_threshold = _convert_threshold(collection.crawler_collection.new_elements_threshold)
        modified_elements_threshold = _convert_threshold(collection.crawler_collection.modified_elements_threshold)
        deleted_elements_threshold = _convert_threshold(collection.crawler_collection.deleted_elements_threshold)

        if new_elements_threshold < len(created_items_uid) or \
           modified_elements_threshold < len(updated_items_uid) or \
           deleted_elements_threshold < len(deleted_items_uid):
            if new_elements_threshold < len(created_items_uid):
                response = u'Too many new elements (%s/%s) in collection %s' % (
                    len(created_items_uid),
                    new_elements_threshold,
                    collection,
                )
                print >> log, smart_str(response)
            if modified_elements_threshold < len(updated_items_uid):
                response = u'Too many modified elements (%s/%s) in collection %s' % (
                    len(updated_items_uid),
                    modified_elements_threshold,
                    collection,
                )
                print >> log, smart_str(response)
            if modified_elements_threshold < len(deleted_items_uid):
                response = u'Too many deleted elements (%s/%s) in collection %s' % (
                    len(deleted_items_uid),
                    deleted_elements_threshold,
                    collection,
                )
                print >> log, smart_str(response)
            success = False
        else:
            success = True
            print >> log, u'Updated elements'

        # create new elements
        for uid in created_items_uid:
            item = dict_new_items[uid]
            item.is_valid = success
            try:
                item.save()
            except IntegrityError:
                item = Item.objects.get(uid=item.uid,
                                        collection=item.collection,
                                        is_valid=success)
            added_items.append(item)

        # update new elements
        for uid in updated_items_uid:
            item = Item.objects.get(uid=uid, collection=collection,
                                    is_deleted=False, is_valid=True)
            new_content = dict_new_items[uid].content
            if success:
                item.update_content(new_content)
                item.save()
            else:
                try:
                    invalid_item = Item.objects.get(uid=uid, collection=collection,
                                                    is_deleted=False, is_valid=False)
                except Item.DoesNotExist:
                    invalid_item = deepcopy(item)
                    invalid_item.id = None
                    invalid_item.is_valid = False

                invalid_item.update_content(new_content)
                invalid_item.save()

            updated_items.append(item)

        # delete obsoletes elements (if proceed)
        if collection.crawler_collection.check_deleted:
            for uid in deleted_items_uid:
                item = Item.objects.get(uid=uid, collection=collection,
                                        is_deleted=False, is_valid=True)
                if success:
                    item.delete()
                else:
                    try:
                        invalid_item = Item.objects.get(uid=uid, collection=collection,
                                                        is_deleted=False, is_valid=False)
                    except Item.DoesNotExist:
                        invalid_item = deepcopy(item)
                        invalid_item.id = None
                        invalid_item.is_valid = False

                    invalid_item.content = u''
                    invalid_item.save()

    return success, log, added_items, updated_items, deleted_items_uid, deleted_items


def create_extraction_report(success, crawler_collection, items_dict, log, crawled_log=''):
    report = Report(
        crawler_collection=crawler_collection,
        crawling_time=crawler_collection.last_crawling_time,
    )
    report.deleted_items_json = items_dict['deleted']
    if success:
        report.return_code = 'suc'
        report.crawled_data = crawled_log
        report.traceback = ''
    else:
        report.return_code = 'err'
        report.traceback = u'%s\n%s' % (smart_unicode(log.getvalue()), crawled_log)
        report.crawled_data = ''
    report.save()
    # adding items to report
    for item in items_dict['added']:
        report.added_items.add(item)
    for item in items_dict['updated']:
        report.updated_items.add(item)


# ----- auxiliar functions -----


def _convert_threshold(value, total=None):
    """Returns an integer with the value. By now only checks
    integers, not percentages"""
    if not value:
        value = ''
    re_res = re.search('^\d+%$', value)
    if re_res != None:  # the expresion match, so remove the trailing '%'
        value = value[:-1]
    if value == '':
        return sys.maxint
    else:
        return int(value)
