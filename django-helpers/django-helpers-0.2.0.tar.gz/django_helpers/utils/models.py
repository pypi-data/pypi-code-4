__author__ = 'ajumell'

from django.db import connection

try:
    import sqlparse
except ImportError:
    sqlparse = None


def query_count():
    return len(connection.queries)


def last_query():
    l = query_count() - 1
    query = connection.queries[l]['sql']
    if sqlparse is not None:
        query = sqlparse.format(query, reindent=True, keyword_case='upper')
    return query