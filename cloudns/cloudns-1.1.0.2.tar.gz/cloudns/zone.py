#!/usr/bin/env python
# coding=utf-8

"""
defines the Zone class.
"""


class Zone(object):
    """a Zone can manage records in the zone easier than a User.

    a Zone has a zone name (self.zone) and a binded user (self.user).

    bulk create/delete records are not defined here, if you wish to use them,
    please use :py:meth:`User.create_records` and
    :py:meth:`User.delete_records`.

    """
    def __init__(self, user, zone_name):
        """create a Zone object.

        Args:
            user: a User object.
            zone_name: zone name.

        """
        self.user = user
        self.zone = zone_name

    def get_all_records(self, offset=0, limit=20):
        """get all records under this zone.

        offset and limit has the same meaning as in MySQL's select statement's
        limit clause. They are used to limit result to a subset.

        Args:
            offset: return records from this index. index is 0-based.
            limit: return this many records. set to -1 to get all records.

        Return:
            json response from server.

        """
        return self.user.get_all_records(self.zone, offset=offset, limit=limit)

    def get_record_count(self):
        """return how many records in this zone.

        .. note::

            you can not rely on this. Because user could have added or deleted
            some records after you call this method.

        """
        return self.user.get_record_count(self.zone)

    def get_record_by_id(self, rid):
        """return one Record for given rid.

        raise RecordNotFound if record not found.

        """
        return self.user.get_record_by_id(self.zone, rid)

    def get_records_by_name(self, name):
        """return a list of Records that exactly match given name.

        """
        return self.user.get_records_by_name(self.zone, name)

    def create_record(self, name, content, isp, type='A', ttl=300):
        """create a new record.

        .. note::

            Create duplicate record will result in DuplicateRecord raised.

        Args:
            name: the host name (a label)
            content: the value
            isp: 'tel' for China Telecom, 'uni' for China Unicom
            type: record type, could be 'A', 'cname' etc
            ttl: time to live, cache/expiration duration in seconds

        """
        return self.user.create_record(self.zone, name, content, isp,
                                       type=type, ttl=ttl)

    def update_record(self, record, auto_retry=False):
        """update record by record.rid.

        Args:
            record: update old record with record.rid to match this record.

        """
        return self.user.update_record(record, auto_retry=auto_retry)

    def delete_record_by_id(self, rid, auto_retry=False):
        """delete record by id.

        if auto_retry is True, continue retry until delete is successful.

        if given rid does not exist, :py:class:`cloudns.RecordNotFound` will be
        raised.

        """
        return self.user.delete_record_by_id(self.zone, rid,
                                             auto_retry=auto_retry)

    def delete_records_by_name(self, name, auto_retry=False):
        """delete all records that match exactly the given name in this zone.

        If auto_retry is True, continue retry until delete is successful.

        If given name does not match any record,
        :py:class:`cloudns.RecordNotFound` will be raised.

        """
        return self.user.delete_records_by_name(self.zone, name,
                                                auto_retry=auto_retry)

    def search_record(self, keyword):
        """return records that is in this zone and matches given keyword.

        You can use * in keyword to match anything. You can use up to two * in
        keyword. consecutive * is not allowed.

        """
        return self.user.search_record(self.zone, keyword)
