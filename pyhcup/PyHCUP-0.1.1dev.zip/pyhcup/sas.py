"""Tools for processing a SAS loadfile (.sas) and a corresponding flat ASCII datafile (fixed-width .asc or .txt).

Originally developed to parse HCUP State Inpatient Database ASCII files (http://www.hcup-us.ahrq.gov/sidoverview.jsp). Untested with other data sources.

Requires pandas (pandas.pydata.org)"""
import re
import pandas as pd
from pandas import Index, Series, DataFrame, Panel

def file_length(target):
    """Reads through a target file and determines its length. Useful for determining whether to chunk large files for actual data loading.
    
    Can still take a while for large files, though this code attempts to minimize required overhead.
    """
    with open(target) as h:
        lines = sum(1 for line in h)
    return lines

def get_meta_sections(target):
    """Parses target SAS loadfile and returns a dict with the lines from 'Variable attribute' and 'INPUT' sections
    """
    #TODO: consider bringing in the regex portions of meta_from_sas()
    #TODO: consider adding regex matching for missing values informat conversions
    #cont'd: this regex should find and capture them INVALUE\s{1}(?P<informat_class>\w+)(?P<informat_map>\s+(\S+ = \S+))+
    handle = open(target)
    var_section_header = '*** Variable attribute ***;'
    input_section_header = '*** Input the variables from the ASCII file ***;'
    
    lines = [line.strip() for line in handle]
    concatenated = ' '.join(lines)
    
    var_section = lines[lines.index(var_section_header)+2:lines.index(input_section_header)]
    
    input_section = lines[lines.index(input_section_header)+2:]
    input_section = input_section[:input_section.index(';')]
    
    lw_pattern = '(LRECL = (?P<line_width>\d+))'
    lw_search = re.search(lw_pattern, concatenated)
    if lw_search:
        line_width = lw_search.groups()[1]
    else:
        raise Exception('Unable to find line width (logical record length aka LRECL) in specified handle')
    
    handle.close()
    
    return {'var': var_section,
            'input': input_section,
            'line_width': line_width
            }

def meta_from_input_chunk(chunk):
    """Expects chunk to be a string. Each string is a trimmed line from the '*** Input the variables from the ASCII file ***;' section of a SAS loadfile
    """
    split = chunk.split()
    meta = {'position': int(split[0].replace('@', '')) - 1,#sas starts column counts at 1; python starts at 0
            'field': split[1],
            'informat': split[2],
            }
    return meta

def meta_from_sas(target):
    """Parses target SAS loadfile and builds a pandas DataFrame object with meta data.
    """
    
    #pull germane lines from sas loadfile
    sections = get_meta_sections(target)
    
    #use variable attribute section mostly to pull descriptive column headings
    pattern = '((?P<field>\S+)\s+LENGTH=\$?(?P<length>\d+)\s*(FORMAT=(?P<format>\S*))?\s*LABEL=\s*"(?P<label>[^"]+)")'
    fields_from_var_att = [x.groupdict() for x in re.finditer(pattern, ' '.join(sections['var']))]
    v_df = DataFrame(fields_from_var_att)
    
    #use input section for starting positions and bulk of format info
    fields_from_input = [meta_from_input_chunk(x) for x in sections['input']]
    i_df = DataFrame(fields_from_input)

    #merge meta information from each section of the sas loadfile
    meta_df = i_df.merge(v_df.drop('length', axis=1), on='field',
                         suffixes=('_input_section', '_var_section'))
    
    #get most of the column widths using the difference between start positions
    #but exclude any width determination for the final column, since we don't have a right-side bound
    starts = [x for x in meta_df['position']]
    widths = [starts[key+1] - value for key, value in enumerate(starts) if key+1<len(starts)]
    
    #determine and append the final column width using the final start position and the total line width
    #this trusts the LRECL value in the loadfile rather than verifying the width of a line in a datafile
    #also another quirk worth noting is that although SAS calls the first column 1, the LRECL value
    #is based on starting at 0
    widths.append(int((sections['line_width'])) - starts[-1])
    
    #add widths back to the dataframe
    meta_df['width'] = widths
    
    return meta_df

def df_from_sas(target, meta_df, skiprows=None, readrows=None):
    """Parses target SAS datafile. Requires a pandas DataFrame object with meta data. Returns a pandas DataFrame object containing the parsed data.

    Can optionally specify rows to skip or limit the number of rows to read.
    """
    widths = [int(x) for x in meta_df.width]
    names = [x for x in meta_df.field]
    df = pd.read_fwf(target, header=None, widths=widths, names=names,
                     nrows=readrows, skiprows=skiprows)
    return df