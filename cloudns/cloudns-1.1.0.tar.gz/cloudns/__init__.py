#!/usr/bin/env python
# coding=utf-8

"""cloudns api python client.

The cloudns API is documented at http://wiki.dev.game.yy.com/moin/DNS

This python client is based on that API.

The major version of this client tries to match the the API version. Thus from
1.1.0, it will support API v1.1.

"""

__version__ = '1.1.0'
__maintainer__ = 'g-yygame-brd@yy.com'


import logging
logging.basicConfig(format='%(levelname)-8s %(message)s',
                    level=logging.INFO)
logger = logging.getLogger('cloudns')

t1 = logging.getLogger('requests')
t1.setLevel(logging.WARNING)


from . import httpclient


API = 'https://cloudns.duowan.com/api/'


class CloudnsError(Exception):
    pass


class CloudnsRuntimeError(CloudnsError, RuntimeError):
    pass


class CloudnsValidationError(CloudnsError):
    pass


class CloudnsBadUsage(CloudnsError):
    pass


def join_by_comma_maybe(obj):
    """join an iterable maybe.

    if obj is a string, do nothing.
    if obj is an iterable, join it with u','.

    """
    if isinstance(obj, basestring):
        result = obj
    else:
        try:
            result = u','.join(obj)
        except TypeError as _:
            raise CloudnsBadUsage(u'join by comma failed: %s' % (obj,))
    return result


class User(object):
    """a User in cloudns admin system.

    A User is identified by his/her passport and is authenticated by a token.

    """
    def __init__(self, passport=None, token=None, api=None):
        self.passport = passport
        self.token = token
        self.api = api or API

    def dnscall(self, method, **kwargs):
        """call a low level cloudns API via HTTP.

        method is the action parameter (a param) in cloudns API.

        """
        kwargs.update(a=method, psp=self.passport, tkn=self.token)
        logger.info('calling %s with %s', method,
                    u', '.join((u'%s=%s' % (k, kwargs[k])
                                for k in kwargs if k != 'tkn')))
        r = httpclient.post(self.api, data=kwargs)
        if r['ok']:
            logger.debug('result is %s', r['json'])
            return r['json']
        else:
            raise CloudnsRuntimeError(r['msg'])

    def get_all_zones(self):
        """return all zones current user has permission.

        """
        return self.dnscall('zone_load_multi')

    def get_zone(self, zone):
        """return zone information for given zone.

        """
        return self.dnscall('zone_check', z=zone)

    def get_zones(self, zones):
        """return zone information for given zones.

        Args:
            zones: an iterable of zones, or comma separated zones as a string.

        """
        zone = join_by_comma_maybe(zones)
        return self.dnscall('zone_check', z=zone)

    def create_zone(self, zone):
        """create a zone.

        """
        return self.dnscall('zone_new', z=zone)

    def delete_zone(self, zone):
        """delete a zone.

        """
        return self.dnscall('zone_delete', z=zone)

    def get_all_records(self, zone, offset=0, limit=100):
        """get all records under this zone.

        offset and limit has the same meaning as in MySQL's select statement's
        limit clause. They are used to limit result to a subset.

        Args:
            offset: return records from this index. index is 0-based.
            limit: return this many records. set to -1 to get all records.

        Return:
            json response from server.

        """
        return self.dnscall('rec_load_all', z=zone,
                            offset=offset, number=limit)

    def get_record_count(self, zone):
        """return how many records is in given zone.

        Note: you can not rely on this. Because user could have added new
        record after you call this method.

        """
        return self.dnscall('rec_load_size', z=zone)

    def get_record(self, zone, rid):
        """get one record.

        """
        return self.dnscall('rec_load', z=zone, rid=rid)

    def add_record(self, zone, name, content, isp, type='A', ttl=300):
        """add a new record.

        """
        return self.dnscall('rec_new', z=zone, name=name, content=content,
                            isp=isp, type=type, ttl=ttl)

    def update_record(self, rid, zone, name, content, isp, type='A', ttl=300):
        return self.dnscall('rec_edit', rid=rid,
                            z=zone, name=name, content=content,
                            isp=isp, type=type, ttl=ttl)

    def delete_record(self, rid):
        return self.dnscall('rec_delete', rid=rid)

    def delete_records(self, rids):
        """delete given records.

        This differs from delete_record because it sends a single request to
        remote server.

        Args:
            rids: an iterable of record ids or comma seperated ids.

        """
        rids = join_by_comma_maybe(rids)
        return self.dnscall('bulk_rec_delete', rids=rids)

    def add_records(self, zone, records):
        """add a list of records to given zone.

        Args:
            records: an iterable of Record object or raw json.
                     if you want to use raw json, see `bulk_rec_new' in
                     cloudns API for more information.

        """
        # TODO support [Record] param.
        return self.dnscall('bulk_rec_new', z=zone, records=records)

    def search_record(self, zone, keyword):
        """search record that is in given zone and matches given keyword.

        You can use * in keyword to match anything. You can use up to two * in
        keyword. consecutive * is not allowed.

        """
        if '*' in keyword:
            if '**' in keyword:
                raise CloudnsBadUsage(u'consective * is not allowed.')
            star_count = count_if(lambda x: x == '*', keyword)
            if star_count > 2:
                raise CloudnsBadUsage(
                    u'only up to two * is allowed. you used %s.' %
                    (star_count,))
            return self.dnscall('rec_load_by_prefix', z=zone, name=keyword)
        return self.dnscall('rec_search', z=zone, k=keyword)

    def get_records_by_name(self, zone, name):
        """search records with given name in given zone.

        """
        return self.dnscall('rec_load_by_name', z=zone, name=name)

    def delete_records_by_name(self, zone, name):
        return self.dnscall('rec_delete_by_name', z=zone, name=name)


class Zone(object):
    PENDING_ACTIVE = 0
    ACTIVE = 1
    PENDING_REMOVAL = 2

    def __init__(self, name=None):
        self.name = name
