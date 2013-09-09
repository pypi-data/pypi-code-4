
import logging

log = logging.getLogger(__name__)

from types import *

from guide import *

import pandas as pd

import math

import json

stripQuotes = lambda s: s.replace('"', '')

class GEOSampleMetadata(object):
    """\
Manage metadata for each sample.   Instance attributes are derived from GSE metadata records
with descriptors that begin with ``!Sample_``.  The first part of this descriptor is stripped 
off to leave just the remainder.   For example, ``!Sample_organism`` becomes *<instance>*``.organism``.

There are a few exceptions.   The *sample_id* attribute is set on instantiation.  The *characteristics*
attribute is derived from ``!Sample_characteristics_ch1``, and it is worth nothing that this is the
attribute that defines the column index levels used in buildng the pandas MultiIndex for the
*GEOSeries* instance's DataFrame attribute.
"""
    def __init__(self, sample_id):
        self.sample_id = sample_id
        self._characteristics = dict()

    @property
    def characteristics(self):
        """\
Column index metadata used to build the pandas *DataFrame* MultiIndex for the columns.
"""
        return self._characteristics

    @property
    def metadata_levels(self):
        """Same thing as "characteristics" property, above.  Haven't decided which I like better."""
        return self._characteristics


    def toJSON(self):
        """\
Returns a dictionary of JSONifiable objects.
"""
        jr = self.__dict__.copy()
        jr['metadata_levels'] = jr.pop('_characteristics')
        return jr
    
    @property
    def attributes(self):
        """\
Attribute names are derived from the GEO series matrix metadata descriptors.   These
begin with ``!Series_`` for series (dataset-wide) metadata, and ``!Sample_`` for
metadata for specific samples.   In *GEOSampleMetadata* instances attributes are set by
using setattr, usually from the *GEOSeriesMetadata* ``parse`` method.
"""
        return filter(lambda x: x if x[0] != '_' else None, self.__dict__.keys())

    def __getstate__(self):
        result = self.__dict__.copy()
        return result

    def __setstate__(self, st):
        self.__dict__ = st



class GEOSeriesMetadata(object):
    """\
Manage metadata for the GEO Series as a whole.   These are metadata that apply to the entire dataset, rather
than just one or a few of its samples.   Information pertaining to the GEO publication as a whole (e.g. pubmed ID)
are referenced as ``!Series_`` items in the metadata header.   The attributes are derived as this instance is
built and attribute names are created by stripping off the ``!Series_`` portion of the descriptor.

Some series metadata rowas may appear more than once, in which case the values associated with the corresponding
attributes are changed from singletons to lists.

Note that ``sample_id`` is actually part of the series metadata and this row is parsed to create a list
of sample IDs that are dereferenced when creating the *GEOSampleMetadata* instances.
"""
    def __init__(self, geo_file):

        self._attribs = list()
        self._samples = dict()
        self._samples_ind = list()

        rows = [ [ y.strip() for y in x.split('\t') ] for x in geo_file ]

        for r in rows:
            # Skip if gthis isn't metadata.
            if len(r) < 2 or r[0][0] != '!': continue

            # Have we reached the end of the metadata?
            if r[0].lower().startswith("!series_matrix_table_begin"): break

            self.parse(r)

            
    def parse(self, tup):
        """\
Parse a row of metadata, split into a tuple along *sep* (TAB character) boundaries.
"""
        
        if tup[0].startswith('!Series_'):  # Process series-level metadata 
            ser_key = tup[0][8:]

            if ser_key == 'sample_id':
                self._samples_ind = stripQuotes(tup[1]).split()
                for i in range(len(self._samples_ind)):
                    self._samples[self._samples_ind[i]] = GEOSampleMetadata(self._samples_ind[i])
            
            else:
                # If there is more than one line with the same
                # metadata attribute name, turn it into a list.
                if ser_key in self._attribs:
                    if isinstance(getattr(self, ser_key), list):
                        getattr(self, ser_key).append(stripQuotes(tup[1]))
                    else:
                        setattr(self, ser_key, [ getattr(self, ser_key), stripQuotes(tup[1]) ])
                else:
                    self._attribs.append(ser_key)
                    setattr(self, ser_key, stripQuotes(tup[1]))

        
        elif tup[0].startswith('!Sample'):  # Process per-sample metadtata
            samp_key = tup[0][8:]
            
            for i in range(1, len(tup)):
                field = stripQuotes(tup[i])
                samp = self._samples[self._samples_ind[i-1]]

                if samp_key.startswith('characteristics_'):
                    t2 = [ x.strip() for x in field.split(':', 1)]
                    if len(t2) > 1:
                        samp._characteristics[t2[0]] = t2[1]
                    
                else:
                    setattr(samp, samp_key, field)
            

    def __getitem__(self, sample_id):
        if isinstance(sample_id, int):
            return self._samples[self._samples_ind[sample_id]]

        elif isinstance(sample_id, slice):
            return  [ self._samples[k] for k in self._samples_ind[sample_id] ]

        else:
            return self._samples[sample_id]


    @property
    def samples(self):
        """\
Returns a generator for iterating through the list of samples in the same order in which
their IDs appear in ``!Series_sample_id`` metadata.
"""
        return (self._samples[self._samples_ind[i]] for i in range(len(self._samples)))

    @property
    def attributes(self):
        """\
Attribute names are derived from the GEO series matrix metadata descriptors.   These
begin with ``!Series_`` for series (dataset-wide) metadata, and ``!Sample_`` for
metadata for specific samples.
"""
        return list(self._attribs)


    def toJSON(self):
        """\
Return a dictionary of JSONifiable objects.
"""
        jr = self.__dict__.copy()
        jr['samples'] = [ s.toJSON() for s in self.samples ]
        jr.pop('_samples')
        jr.pop('_samples_ind')
        return jr


    
def cvt(s, log2=False):
    try:
        return math.log(float(s), 2) if log2 else float(s)
    except:
        return stripQuotes(s)
    

class GEOSeries(object):
    """\
Container for GEO Series Experiments (GSE) datasets.
"""

    def __init__(self, geo_file, sep='\t', log2=False):
        
        self._meta = GEOSeriesMetadata(geo_file)
    
        self.parse(geo_file, log2=log2)

    def parse(self, geo_file, sep='\t', log2=False):
        """\
Injest TSV rows from *geo_file* and turn them into
a `pandas` DataFrame.
"""
        # Rewind and skip everything up to the start of actual data
        geo_file.seek(0)
        while not geo_file.readline().startswith("!series_matrix_table_begin"):  pass

        # First line in the matrix_table section will be the column labels.
        col_names = [ stripQuotes(cn.strip()) for cn in geo_file.readline().split(sep) ]

        # Read and parse until we come to theend.
        result = list()
        for row in geo_file:
            if row.startswith('!series_matrix_table_end'): continue
            tup = row.split(sep)
            result.append([ stripQuotes(tup[0]) ] + map(lambda y: cvt(y.strip(), log2), tup[1:]))
            

        # Make a DataFrame out of it, set the index to the probe ID column (first column)
        self._df = pd.DataFrame(result, columns=col_names)
        self._df = self._df.set_index([col_names[0]], drop=True)

        # Create a MultiIndex for the columns.  Each level is a column metadata item.  Level 0 is just the sample ID.
        level_names =  self._meta[0].characteristics.keys()
        level_values = [ ([ s.sample_id ] + [ s.characteristics.get(k, '') for k in level_names]) \
                             for s in self._meta.samples if s.sample_id in col_names ]
        level_names.insert(0, 'sample_id')
        self._df.columns = pd.MultiIndex.from_tuples(level_values, names=level_names)

        
    @property
    def metadata(self):
        return self._meta

    def to_tsv(self, tsv_file, level=0, axis=1, sep='\t'):
        """\
Emits a tab-separated version (TSV) of the dataset.   By default all columns
are emitted individually.  If *level* is specified, columns will be grouped and aggregated
(using the *DataFrame.mean* method) according to the headings for that level.
"""
        outf = tsv_file if isinstance(tsv_file, FileType) else open(tsv_file, 'w')
        result = self.mean(axis=axis, level=level)
        result.to_csv(outf, sep=sep)

    def mean(self, level=0, axis=1, aggfn=None):
        """\
Group and agregate columns according to the column headings at the specified *level*.
"""
        g1 = self._df.groupby(level=level, axis=axis)
        return g1.mean()

    @property
    def column_index_levels(self):
        return self._df.columns.names


