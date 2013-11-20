"""Tools for processing HCUP SID meta and data frames.

Provides additional functionality specific to HCUP SID files beyond the SAS parsing provided by the sas_import module."""
import re
import numpy as np
import pandas as pd
from pandas import Index, Series, DataFrame, Panel

def replace_df_sentinels(df, extra_dict=None):
    """Replaces HCUP SID sentinel patterns and values for bad data
    
    Definitions from http://www.hcup-us.ahrq.gov/db/coding.pdf
    """
    patterns = {
        'missing':        '(-9+| |\.)',
        'invalid':        '(-8+|A)',
        'unavailable':    '(-7+)',
        'inconsistent':   '(-6+)',
        'notapplicable':  '(-5+)',
        }
    if extra_dict is not None:
        patterns.update(extra_dict)
    
    sentinels_regex = re.compile('^%s$' % '|'.join(patterns.values()))
    df = df.applymap(lambda x: np.NaN if re.match(sentinels_regex, str(x)) is not None else x)
    return df

def replace_df_placeholders(df, extra_dict=None):
    dictionary = {'Y': 1, 'N': 0}
    if extra_dict is not None:
        dictionary.update(extra_dict)
        
    df = df.applymap(lambda x: dictionary.get(x) if x in dictionary else x)
    return df

#def replace_yn(df):
#    #replaces 'Y' and 'N' characters used as placeholders for boolean columns



def augment_meta_df(meta_df):
    """Uses informat data pulled from SAS loadfile to derive additional information about columns
    
    Returns: processed meta dataframe.
    """
    meta_df['length'] = meta_df['informat'].map(lambda x: col_from_invalue(x)['length'])
    meta_df['data_type'] = meta_df['informat'].map(lambda x: col_from_invalue(x)['type'])
    meta_df['scale'] = meta_df['informat'].map(lambda x: col_from_invalue(x)['scale'])
    return meta_df

def col_from_invalue(invalue):
    """Takes an HCUP SID invalue name and infers details on appropriate database column type.

    With a single exception the INFORMAT definitions in the *CORE.sas files are actual invalue vars declared earlier. Fortunately those invalue variables appear to use a standardized naming convention that infers the type and formatting of the data in that column.

    The exception is KEY fields, which use a true SAS INFORMAT definition but which are all integers anyways.

    Returns a dictionary with column type details.
    """
    result = {'invalue': invalue}
    result['scale'] = False #default
    key_regex = re.compile('(?P<length>\d+).')
    numeric_regex = re.compile('(N(?P<full_length>\d+)P(?P<scale>\d*)F)')
    char_regex = re.compile('\$CHAR(?P<length>\d+)')
    
    key_capture = re.search(key_regex, invalue)
    numeric_capture = re.search(numeric_regex, invalue)
    char_capture = re.search(char_regex, invalue)

    if char_capture is not None:
        groups = char_capture.groupdict()
        result['type'] = 'char'
        result['length'] = int(groups['length'])
        
    elif numeric_capture is not None:
        groups = numeric_capture.groupdict()
        
        #at this point some adjustments have to be made
        #the full_length value includes a position for sign and a decimal, if needed
        result['length'] = int(groups['full_length'])# - 1  #unpad from sign #commented out because it is shorting the length
        if groups['scale'] == '':
            result['scale'] = 0
        else:
            result['scale'] = int(groups['scale'])
        
        if result['scale'] > 0:
            #there will be a decimal point, so we need to subtract another 1 from full_length to get sigfigs
            result['length'] -= 1
            result['type'] = 'numeric'
        else:
            result['type'] = 'int'
    elif key_capture is not None:
        result['length'] = int(key_capture.groupdict()['length'])
        result['type'] = 'int'#TODO: add support for bigint for key and any other lengthy ints
    
    else:
        raise Exception('Unable to to determine column type details. %s is not numeric, character, or key field.' % (invalue))
    
    return result