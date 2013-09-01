import json
import os
import time

from boto import ec2
from boto import dynamodb
from boto.dynamodb.condition import BEGINS_WITH
from boto.dynamodb.exceptions import DynamoDBKeyNotFoundError

from awsjuju.lock import Lock


class RetryLater(Exception):
    pass


class InvalidConfig(Exception):
    pass

NotFound = DynamoDBKeyNotFoundError


class BaseController(object):

    _ec2 = _dynamodb = _lock_table = _config = None
    _data_table = _table_name = _lock_table = _table_options = None

    # We share the lock table among all services.
    _lock_table_name = "awsjuju-manage-locks"
    _lock_table_options = {
        'hash': 'key',
        'throughput': (50, 10)}

    query_begins = BEGINS_WITH

    @classmethod
    def main(cls, op):
        try:
            method = getattr(cls(), "on_%s" % op)
            print "Invoking", method
            return method()
        except RetryLater:
            return

    def get_config(self):
        """Get the service configuration.
        """
        if self._config:
            return self._config

        data = self.unit.config_get()
        key = data['access-key-id']
        secret = data['secret-access-key']

        if not key or not secret:
            self.unit.log("No credentials set")
            raise InvalidConfig()

        self._config = data
        return data

    def get_credentials(self):
        """Get the provider iam credentials.
        """
        data = self.get_config()
        return dict(
            aws_access_key_id=data['access-key-id'],
            aws_secret_access_key=data['secret-access-key'])

    def get_ec2(self):
        """ Retrieve a connection to ec2.

        Access requirements depend on service in question.
        """
        if self._ec2:
            return self._ec2
        self._ec2 = ec2.connect_to_region(
            self.get_region(), **(self.get_credentials()))
        return self._ec2

    def get_region(self):
        """Get the region being operated on.
        """
        return self.unit.ec2metadata['availability-zone'][:-1]

    def get_lock(self, key, ttl=20, delay=10, attempts=3):
        """Obtain a resource lock on key for the specified duration/ttl.

        Lock acquisition will make up to arg: attempts number of tries
        to acquire the lock and will sleep for arg: delay seconds between
        attempts.
        """
        if not self._lock_table:
            self._lock_table = self._get_table(
                self._lock_table_name, self._lock_table_options)
        return Lock(
            self._dynamodb, self.unit.unit_name, self._lock_table,
            key, ttl, delay, attempts)

    def get_db(self):
        """Get the data table for the controller.
        """
        if not self._dynamodb:
            self._dynamodb = dynamodb.connect_to_region(
                self.get_region(), **(self.get_credentials()))

        if self._data_table is not None:
            return self._data_table

        if self._table_name is None or self._table_options is None:
            raise RuntimeError(
                "Db requested but table not specified %s",
                self.__class__.__name__)
        self._data_table = self._get_table(
            self._table_name, self._table_options)
        return self._data_table


def get_or_create_table(dynamodb, name, options):
    """Get or create a table.
    """
    if name in dynamodb.list_tables():
        return dynamodb.get_table(name)

    params = [options['hash'], str]
    if options.get('range'):
        params.extend([options['range'], str])

    table = dynamodb.create_table(
        name,
        dynamodb.create_schema(*params),
        *options['throughput'])

    # Wait till the table is ready to use, about 15s
    while True:
        if table.status != 'ACTIVE':
            time.sleep(4)
            table.refresh()
            continue
        break
    return table


class KVFile(object):

    def __init__(self, path):
        self.path = path

    def _load(self):
        if not os.path.exists(self.path):
            return {}

        with open(self.path) as fh:
            return json.load(fh)

    def get(self, key):
        return self._load().get(key)

    def get_all(self):
        return self._load()

    def set(self, key, value):
        data = self._load()

        with open(self.path, "w") as fh:
            data[key] = value
            json.dump(data, fh, indent=2)

    def remove(self, key):
        data = self._load()

        with open(self.path, "w") as fh:
            if key in data:
                del data[key]
            json.dump(data, fh, indent=2)
