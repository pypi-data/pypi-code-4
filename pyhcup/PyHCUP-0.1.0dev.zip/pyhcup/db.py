"""Tools for getting HCUP SID data into a database

"""
import re
#import pandas as pd
#from pandas import Index, Series, DataFrame, Panel

def column_clause(dictionary):
    """Builds a SQL column definition from information in a dictionary record
    
    """
    name = dictionary['field']
    length = int(str(dictionary['length']).replace('L', ''))
    
    if name == 'KEY':
        constraint = 'NOT NULL PRIMARY KEY'
    elif 'null_type' in dictionary and dictionary['null_type'] == False:
        constraint = 'NOT NULL'
    else:
        constraint = 'NULL'
    
    if dictionary['data_type'] == 'char':
        data_type = 'VARCHAR(%s)' % length
    elif dictionary['data_type'] == 'numeric':
        data_type = 'NUMERIC(%s, %s)' % (length, dictionary['scale'])
    elif dictionary['data_type'] == 'int' and length > 9:
        data_type = 'BIGINT'
    else: #fallback
        data_type = dictionary['data_type']
    
    clause = '%s %s %s' % (name, data_type, constraint)
    return clause