#!/usr/bin/python
#
# Copyright (C) 2010 Google Inc.

""" Fusion Tables Client.

Issue requests to Fusion Tables.
"""

__author__ = 'kbrisbin@google.com (Kathryn Brisbin)'

# standard libraries
import logging
#import time
#import pprint
from csv import DictReader
from StringIO import StringIO

# site packages

# local packages
import urllib2, urllib
#try:
#  import oauth2
#  import authorization.oauth
#except: pass
from sql.sqlbuilder import SQL

import httplib2
from apiclient.discovery import build
from oauth2client.client import SignedJwtAssertionCredentials
from oauth2client.client import AccessTokenRefreshError

class FTClientError():
  def __init__(self, message, code):
    self.message = message
    self.code = code
  def __str__(self):
    return repr(self.message)


class FTClient():

  def _get(self, query): pass
  def _post(self, query): pass

  def query(self, ft_query, request_type=None):
    """ Issue a query to the Fusion Tables API and return the result. """
    logging.debug ('FT QUERY: %s'%ft_query)

    #encode to UTF-8
    try: query = ft_query.encode("utf-8")
    except: query = ft_query.decode('raw_unicode_escape').encode("utf-8")

    if request_type is None:
        lowercase_query = query.lower()
        if lowercase_query.startswith("select") or \
            lowercase_query.startswith("describe") or \
            lowercase_query.startswith ("show"):
            request_type = "GET"
        else:
            request_type = "POST"
    try:
        if request_type == "GET":
            return self._get(urllib.urlencode({'sql': query}))
        else:
            return self._post(urllib.urlencode({'sql': query}))
    except urllib2.HTTPError as e:
        raise FTClientError("FT Query Failed:\n  %s\n  %s" % (ft_query, e.msg), e.code)

#    retry=0
#    err = None
#    max_retry = 3
#    while retry < max_retry:
#        try:
#            if request_type == "GET":
#              return self._get(urllib.urlencode({'sql': query}))
#            else:
#              return self._post(urllib.urlencode({'sql': query}))
#        except urllib2.HTTPError as e:
#            if e.code == 500:
#                retry += 1
#                logging.warning ("Recieved %s error - retry %s" % (e.code, retry))
#                err = e
#            elif e.code == 400:
#                raise FTClientError("FT Query Failed:\n  %s\n  %s" % (ft_query, e.msg), e.code)
#            else:
#                raise e
#        if retry < max_retry:
#            logging.info ("waiting %s seconds before retry" % (retry))
#            time.sleep(retry)
#    raise err

#  def insertRowsWithRetry (self, table_id, rows, unique_id_field):
#    # attempt to inser the given rows
#    # if a 500 retry error occurs - the rows may or may not have been
#    # successfully inserted, so wait for a bit and then try again
#    # with insertOrReplace
#    try:
#        return self.insertRows(table_id, rows)
#    except FTClientError as e:
#        if e.code != 500:
#            raise
#         logging.warning ("Recieved %s error on insert - retrying with insertOrReplace" % (e.code, retry))
#    time.sleep (1)
#    return self.insertOrReplace (table_id. rows, unique_id_field, insert_only=True)
#

  def insertRows (self, table_id, rows):
    # insert one or more rows into a fusion table
    # rows may be either a dict containing a single record or a list containing
    # one or more dicts each of which is a single row
    #
    # Returns the given set of rows with a field added with key 'ROWID'
    # containg the new ROWID resulting from the insert
    if rows:
        queries = []
        if isinstance (rows, dict):
            queries.append(SQL().insert(table_id, rows))
        else:
            for row in rows:
                queries.append(SQL().insert(table_id, row))

        full_query = ';'.join(queries)
        logging.debug ("  Inserting %s rows" % (len(queries)))
        result = self.query(full_query)
        logging.debug ('INSERT RESULT: %s'%result)
        #rowids = self.csv2Dict(result)
        rowids = [r[0] for r in result['rows']]

        if len(rowids) <> len(queries):
            logging.warning ("    inserted %s rows but only got back %s rowids" % (len(queries), len(rowids)))

        if isinstance (rows, dict):
            rows.update (rowids[0])
        else:
            for row, rowid in zip(rows, rowids):
                #row.update (rowid)
                row['rowid'] = rowid

    return rows


  def csv2Dict (self, csv):
    # convert a CSV as returned by a fusion table to an array of Dicts, one dict per row
    rows = []
    for row in DictReader(StringIO(csv)):
        rows.append(row)
    return rows


  def updateRow (self, table_id, row, rowid=None):
    # update a row in a fusion table
    # row is a dict containing all the fields to update
    # if rowid is not passed into the method, it must be present in the row dict

    self.query(SQL().update(table_id, row, rowid or row['ROWID']), "POST")


  def updateRows (self, table_id, rows):
    # update an array of row dicts
    # Note that each row must contain a field 'ROWID'
    for row in rows:
        self.updateRow(table_id, row)
    return rows

  def insertOrReplaceRows (self, table_id, rows, unique_id_field, insert_only=False):
    rows = self.getRowIds (table_id, rows, unique_id_field)
#    logging.debug("Found %s records that already exist in FT" % len(rows))

    update_rows = []
    insert_rows = []

    for row in rows:
        if row['rowid']:
            update_rows.append(row)
        else:
            insert_rows.append(row)
    if insert_only:
        rows = update_rows
        if len(update_rows):
	        logging.warning ('Skipping: %s rows that already exist'%len(update_rows))
    else:
       rows = self.updaterows (table_id, update_rows)

    rows.extend(self.insertRows (table_id, insert_rows))

    return rows

  def getRowIds (self, table_id, rows, unique_id_field):
    # get the fusion table rowids corresponding to the given rows
    # unique_id_field is the name of the field containing the unique id which
    # will be used to identify the row
    #
    # Returns the given set of rows, with a new key 'rowid' added containing the
    # rowid correspoding to that unique id value.  If no rowid exists with that
    # unique id, then the ROWID key is added with a value of None

    unique_id_type = type(rows[0][unique_id_field])

    unique_ids = []
    if isinstance (rows, dict):
        unique_ids.append (str(rows[unique_id_field]))
    else:
        for row in rows:
            unique_ids.append (str(row[unique_id_field]))

    ft_query= "SELECT ROWID, '%s' FROM %s WHERE %s IN ( %s )" \
         % (unique_id_field, table_id, unique_id_field, ", ".join(unique_ids))
    result = self.query(ft_query)
    logging.debug ('GetRowIDs: %s'%result)

    rowids = self.csv2Dict(result)

    rowid_map = {}
    # build a lookup table of unique_id to rowid
    for rowid in rowids:
        rowid_map[unique_id_type(rowid[unique_id_field])] = rowid['rowid']

    for row in rows:
        row['rowid'] = rowid_map.get(row[unique_id_field])

    return rows


  def deleteRow (self, row=None, rowid=None):
    # delete the row with the given rowid
    # if you pass a dict then it must contain a key 'ROWID' containing the rowid
    # or you can pass just the rowid

    pass

class ServiceAccountFTClient(FTClient):
    def __init__(self, client_id, key, alt='json'):
        self.client_id = client_id
        self.key = key
        self.scope = 'https://www.googleapis.com/auth/fusiontables'
        self.alt = alt  # alt is ignored
        self.authorize()

    def authorize(self):
        # Create an httplib2.Http object to handle our HTTP requests and
        # authorize it with the Credentials. Note that the first parameter,
        # service_account_name, is the Email address created for the Service
        # account. It must be the email address associated with the key
        # that was created.
        credentials = SignedJwtAssertionCredentials(
            self.client_id, #'141491975384@developer.gserviceaccount.com',
            self.key,
            scope = self.scope)
        http = httplib2.Http(disable_ssl_certificate_validation=True)
        http = credentials.authorize(http)
        self.service = build("fusiontables", "v1", http=http)
                #developerKey='YOUR KEY HERE FROM API CONSOLE'
    def query(self, ft_query):
        logging.debug ('FT QUERY: %s'%ft_query)

        #encode to UTF-8
        try: query = ft_query.encode("utf-8")
        except: query = ft_query.decode('raw_unicode_escape').encode("utf-8")

        # send request
        try:
            result = self.service.query().sql(sql=query).execute()
        except AccessTokenRefreshError:
            logging.info ("Credentials rejected.  Attempting to re-authorize.")
            self.authorize()
            result = self.service.query() .sql(sql=query) .execute()
        print "Query result:", result
        return result

class APIKeyFTClient(FTClient):

  def __init__(self, key):
    self.apikey = key
    self.request_url = "https://www.googleapis.com/fusiontables/v1/query"

  def _get(self, query):
    key = urllib.urlencode({'key': self.apikey})
    url = "%s?%s&%s&alt=csv" % (self.request_url, query, key)
    serv_req = urllib2.Request(url=url)#, headers=headers)

    serv_resp = urllib2.urlopen(serv_req)
    return serv_resp.read()

  def _post(self, query):
    headers = {
      'Content-Type': 'application/x-www-form-urlencoded',
    }

    key = urllib.urlencode({'key': self.apikey})
    url = "%s?%s" % (self.request_url, key)
    serv_req = urllib2.Request(url=url, data=query, headers=headers)
    serv_resp = urllib2.urlopen(serv_req)
    return serv_resp.read()


class ClientLoginFTClient(FTClient):

  def __init__(self, token):
    self.auth_token = token
    self.request_url = "https://www.google.com/fusiontables/api/query"

  def _get(self, query):

#    logging.debug("GET %s"%query)
    headers = {
      'Authorization': 'GoogleLogin auth=' + self.auth_token,
    }
    serv_req = urllib2.Request(url="%s?%s" % (self.request_url, query),
                               headers=headers)

    serv_resp = urllib2.urlopen(serv_req)
    return serv_resp.read()

  def _post(self, query):
#    logging.debug("POST %s"%query)
    headers = {
      'Authorization': 'GoogleLogin auth=' + self.auth_token,
      'Content-Type': 'application/x-www-form-urlencoded',
    }

    serv_req = urllib2.Request(url=self.request_url, data=query, headers=headers)
    serv_resp = urllib2.urlopen(serv_req)
    return serv_resp.read()

#
#class OAuthFTClient(FTClient):
#
#  def __init__(self, consumer_key, consumer_secret, oauth_token, oauth_token_secret):
#    self.consumer_key = consumer_key
#    self.consumer_secret = consumer_secret
#    self.token = oauth2.Token(oauth_token, oauth_token_secret)
#
#    self.scope = "https://www.google.com/fusiontables/api/query"
#
#
#  def _get(self, query):
#    logging.debug("GET %s"%query)
#    consumer = oauth2.Consumer(self.consumer_key, self.consumer_secret)
#    client = oauth2.Client(consumer, self.token)
#    resp, content = client.request(uri="%s?%s" % (self.scope, query),
#                         method="GET")
#    return content
#
#
#  def _post(self, query):
#    logging.debug("POST %s"%query)
#    consumer = oauth2.Consumer(self.consumer_key, self.consumer_secret)
#    client = oauth2.Client(consumer, self.token)
#    resp, content = client.request(uri=self.scope,
#                                   method="POST",
#                                   body=query)
#    return content
#
#

