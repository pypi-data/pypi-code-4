#!/usr/bin/env python
# coding=utf-8

"""
defines the User class
"""

import time

from .utils import count_if
from .base import *
from .record import Record
from .zone import Zone


API = 'https://cloudns.duowan.com/api/'
RETRY_INTERVAL = 0.5


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


def _check_res(res):
    """check whether given res is a good res.

    raise exceptions if res is bad or res['result'] is not 'success'.

    """
    if type(res) is not dict or 'result' not in res:
        raise CloudnsServerError(
            u'expect server response be a dict with result key. found %s' %
            (res,))
    if res['result'] != 'success':
        msg = res['msg']
        if 'not found record' in msg:
            raise RecordNotFound()
        elif 'host not exists' in msg:
            raise RecordNotFound()
        elif 'the same record has existed there' in msg:
            raise DuplicateRecord(u'', res)
        elif 'the record is in updating status, try later' in msg:
            raise RecordNotReady()
        raise CloudnsRuntimeError(res['msg'])


def _record(res):
    """convert a response from cloudns api server to a Record object.

    if there is no record in res, return None.

    This function expects and converts one record to one Record object.
    see :py:func:`_records` if you have many records.

    """
    try:
        obj = res['response']['rec']['obj']
        return Record(**obj)
    except KeyError:
        raise RecordNotFound()


def _records(res):
    """convert a response from cloudns api server to a list of Records.

    if there is no record in res, return [].

    """
    try:
        objs = res['response']['recs']['objs']
        return [Record(**obj) for obj in objs]
    except KeyError:
        return []


def _count(res):
    try:
        return res['response']['count']
    except KeyError:
        raise CloudnsServerError(u'No response.count found', res)


class User(object):
    """a User in cloudns admin system.

    A User can manage any zone or record it has permission with.

    A User is identified by his/her passport and is authenticated by a token.

    """
    def __init__(self, passport=None, token=None, api=None):
        self.passport = passport.strip()
        self.token = token.strip()
        self.api = api or API

    def _dnscall(self, method, **kwargs):
        """call a low level cloudns API via HTTP.

        method is the action parameter (a param) in cloudns API.

        """
        from . import httpclient
        kwargs.update(a=method, psp=self.passport, tkn=self.token)
        logger.info('calling %s with %s', method,
                    u', '.join((u'%s=%s' % (k, kwargs[k])
                                for k in kwargs if k != 'tkn')))
        r = httpclient.post(self.api, data=kwargs)
        if r['ok']:
            logger.info('result is %s', r['json'])
            res = r['json']
            _check_res(res)
            return res
        else:
            raise CloudnsRuntimeError(r['msg'])

    def zone(self, zone):
        """return a Zone object under this User.

        Create a zone object and call methods on it so that you don't have to
        pass the zone parameter all the time.

        """
        return Zone(user=self, zone_name=zone)

    def get_all_zones(self):
        """return all zones current user has permission.

        """
        return self._dnscall('zone_load_multi')

    def get_zone(self, zone):
        """return zone information for given zone.

        """
        return self._dnscall('zone_check', z=zone)

    def get_zones(self, zones):
        """return zone information for given zones.

        Args:
            zones: an iterable of zones, or comma separated zones as a string.

        """
        zone = join_by_comma_maybe(zones)
        return self._dnscall('zone_check', z=zone)

    def create_zone(self, zone):
        """create a zone.

        """
        return self._dnscall('zone_new', z=zone)

    def delete_zone(self, zone):
        """delete a zone.

        """
        return self._dnscall('zone_delete', z=zone)

    def get_all_records(self, zone, offset=0, limit=20):
        """get some/all records under this zone.

        offset and limit has the same meaning as in MySQL's select statement's
        limit clause. They are used to limit result to a subset.

        If you don't pass in offset and limit, default behavior is fetch first
        20 records.

        Args:
            offset: return records from this index. index is 0-based.
            limit: return this many records. set to -1 to get all records.

        Return:
            json response from server.

        """
        return self._dnscall('rec_load_all', z=zone,
                             offset=offset, number=limit)

    def get_record_count(self, zone):
        """return how many records is in given zone.

        .. note::

            you can not rely on this. Because user could have added or deleted
            some records after you call this method.

        """
        r = self._dnscall('rec_load_size', z=zone)
        return _count(r)

    def get_record_by_id(self, zone, rid):
        """return one Record for given rid or raise RecordNotFound.

        """
        r = self._dnscall('rec_load', z=zone, rid=rid)
        return _record(r)

    def get_records_by_name(self, zone, name):
        """return a list of Records that exactly match given name.

        """
        r = self._dnscall('rec_load_by_name', z=zone, name=name)
        return _records(r)

    def create_record(self, zone, name, content, isp, type='A', ttl=300):
        """create a new record.

        .. note::

            Create duplicate record will result in DuplicateRecord raised.

        Args:
            zone: zone name
            name: the host name (a label)
            content: the value
            isp: 'tel' for China Telecom, 'uni' for China Unicom
            type: record type, could be 'A', 'cname' etc
            ttl: time to live, cache/expiration duration in seconds

        """
        r = self._dnscall('rec_new', z=zone, name=name, content=content,
                          isp=isp, type=type, ttl=ttl)
        return _record(r)

    def create_records(self, zone, records):
        """add a list of records to given zone.

        records example::

            [{"type": "A",
              "name": "test1",
              "content": "1.2.3.4",
              "isp": "tel",
              "ttl": 300},
             {"type": "A",
              "name": "test1",
              "content": "1.2.3.4",
              "isp": "uni",
              "ttl": 300}]

        Args:
            records: a python object or a json string. In either case, it
                     should be a list of objects with these keys: type, name,
                     content, isp, ttl.

        """
        if isinstance(records, dict):
            import json
            records = json.dumps(dict)
        if not isinstance(records, basestring):
            raise CloudnsBadUsage(u'create_records: bad records param',
                                  records)
        if not records:
            raise CloudnsBadUsage(
                u'create_records: records param should not be empty', records)
        return self._dnscall('bulk_rec_new', z=zone, records=records)

    def update_record_raw(self, rid, zone, name, content, isp, type, ttl,
                          auto_retry=False):
        """update record with given rid.

        You should usually use :py:meth:`update_record` instead of this
        method.

        """
        record = Record(rid=rid, z=zone, name=name, content=content,
                        isp=isp, type=type, ttl=ttl)
        return self.update_record(record, auto_retry)

    def update_record(self, record, auto_retry=False):
        """update record by record.rid.

        To update a record, first fetch a record with
        :py:meth:`get_records_by_name` or :py:meth:`get_record_by_id`, then
        call :py:meth:`Record.update`, finally :py:meth:`User.update_record`
        or :py:meth:`Zone.update_record`.

        Here is an example::

            >>> old_record = zone.get_record_by_id(rid)
            >>> new_record = old_record.update(content="1.2.3.4")
            >>> zone.update_record(new_record)

        Args:
            record: update old record with record.rid to match this record.

        """
        while True:
            try:
                return self._dnscall('rec_edit', rid=record.rid,
                                     z=record.z, name=record.name,
                                     content=record.content,
                                     isp=record.isp, type=record.type,
                                     ttl=record.ttl)
            except RecordNotReady:
                if auto_retry:
                    time.sleep(RETRY_INTERVAL)
                else:
                    raise

    def delete_record_by_id(self, zone, rid, auto_retry=False):
        """delete record by id.

        if auto_retry is True, continue retry until delete is successful.

        if given rid does not exist, py:class:`cloudns.RecordNotFound` will be
        raised.

        """
        while True:
            try:
                return self._dnscall('rec_delete', z=zone, rid=rid)
            except RecordNotReady:
                if auto_retry:
                    time.sleep(RETRY_INTERVAL)
                    # then continue
                else:
                    raise

    def delete_records_by_name(self, zone, name, auto_retry=False):
        """delete all records that match exactly the given name in given zone.

        If auto_retry is True, continue retry until delete is successful.

        If given name does not match any record,
        py:class:`cloudns.RecordNotFound` will be raised.

        """
        while True:
            try:
                return self._dnscall('rec_delete_by_name', z=zone, name=name)
            except RecordNotReady:
                if auto_retry:
                    time.sleep(RETRY_INTERVAL)
                    # then continue
                else:
                    raise

    def delete_records(self, rids):
        """delete records matching given rids.

        This differs from delete_record because it sends a single request to
        remote server.

        Delete a record that is in PENDING_ACTIVE status will raise
        RecordNotReady exception. This is how the cloudns API works.

        Args:
            rids: an iterable of record ids or comma seperated ids.

        """
        rids = join_by_comma_maybe(rids)
        return self._dnscall('bulk_rec_delete', rids=rids)

    def search_record(self, zone, keyword):
        """return records that is in given zone and matches given keyword.

        You can use * in keyword to match anything. You can use up to two * in
        keyword. consecutive * is not allowed.

        Return:
            a list of Records.

        """
        if '*' in keyword:
            if '**' in keyword:
                raise CloudnsBadUsage(u'consective * is not allowed.')
            star_count = count_if(lambda x: x == '*', keyword)
            if star_count > 2:
                raise CloudnsBadUsage(
                    u'only up to two * is allowed. you used %s.' %
                    (star_count,))
            r = self._dnscall('rec_load_by_prefix', z=zone, name=keyword)
            return _records(r)
        r = self._dnscall('rec_search', z=zone, k=keyword)
        return _records(r)
