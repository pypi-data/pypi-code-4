
from __init__ import *

import sys
import csv
import json

from pprint import pprint

from config import Configurator

log_levels = {'DEB': logging.DEBUG,
              'INF': logging.INFO,
              'WAR': logging.WARN,
              'ERR': logging.ERROR,
              'CRI': logging.CRITICAL,
              'FAT': logging.FATAL,
              }

from matricks import *
from cPickle import *

default_cfg = """\
# These correspond to columns of same name in guide.dataset table
dataset_handle = lambda go: go.metadata.geo_accession
dataset_version = lambda go: '1.0'
dataset_description = lambda go: go.metadata.title
dataset_microarray_description = lambda go: ''
dataset_pubmed_id = lambda go: go.metadata.pubmed_id

# These correspond to columns of same name in guide.sample table.
sample_description     = lambda s: ''
sample_surface_markers = lambda s: ''
sample_notes           = lambda s: ''
sample_tissue_id       = lambda s: 0    # NOTE: This value must be found in guide.tissue table!
sample_cell_lineage    = lambda s: ''
sample_lineage_score   = lambda s: 0
sample_old_sample_id   = lambda s: ''
sample_cmyk_colour     = lambda s: ''
sample_excluded        = lambda s: 'f'

"""

def getHandleAndVersion(gseObj, opts):
    """\
Return strings containing a dataset identifier (or *handle*) and version.   Value
is derived from ``--handle=`` (``--version``) value, if present.  Otherwise, 
`dataset_handle` and `dataset_version` functions are invoked.  If these are empty strings,
the hard defaults are ``dataset`` and ``1.0``.
"""
    handle = opts.handle if opts.handle else (opts.dataset_handle(gseObj) if opts.dataset_handle(gseObj) else 'dataset')
    version = opts.version if opts.version else (opts.dataset_version(gseObj) if opts.dataset_version(gseObj) else '1.0')
    return handle, version


def configure(cfgObj):
    """\
Addes configuration elements to an existing *ConfigParser* object `cfgObj`.
"""
    cfgObj.add_option('dataset_handle')
    cfgObj.add_option('dataset_version')
    cfgObj.add_option('dataset_description')
    cfgObj.add_option('dataset_microarray_description')
    cfgObj.add_option('dataset_pubmed_id')

    cfgObj.add_option('sample_description')
    cfgObj.add_option('sample_surface_markers')
    cfgObj.add_option('sample_notes')
    cfgObj.add_option('sample_tissue_id')
    cfgObj.add_option('sample_cell_lineage')
    cfgObj.add_option('sample_lineage_score')
    cfgObj.add_option('sample_old_sample_id')
    cfgObj.add_option('sample_cmyk_colour')
    cfgObj.add_option('sample_excluded')
    

    cfgObj.add_file(content=default_cfg, type='py')


def createMatricksPickles(gseObj, opts, ctLevel=1, sampleLevel=0):
    """\
Creates the *SampleSignalProfiles* and *CelltypeSignalProfiles* pickled `Matricks`
files used by `Guide`. 

The files will be named ``SampleSignalProfile.``*handle*``.pickled`` and
``CelltypeSignalProfile.``*handle*``.pickled``.   The grouping used for the
celltype file is determined by ctLevel.  Samples are "grouped" by level 0, but this can
be changed by specifying `sampleLevel`.   
"""
    samples = gseObj.mean(level=sampleLevel)
    celltypes = gseObj.mean(level=ctLevel)

    s_list = list(samples.itertuples()) 
    s_list.insert(0, [ 'probeId' ] + list(samples.columns))

    c_list = list(celltypes.itertuples())
    c_list.insert(0, ['probeId' ] + list(celltypes.columns))

    sm = Matricks(s_list)
    cm = Matricks(c_list)

    handle, version = getHandleAndVersion(gseObj, opts)

    cPickle.dump(sm, open('SampleSignalProfiles.{0}.{1}.pickled'.format(handle, version), 'w'), -1)
    cPickle.dump(cm, open('CelltypeSignalProfiles.{0}.{1}.pickled'.format(handle, version), 'w'), -1)


def createDDL(gseObj, opts, ctLevel=1, sampleLevel=0):
    """\
Emit DDL for populating the ``dataset`` and ``sample`` tables in the *guide* database.
"""
    handle, version = getHandleAndVersion(gseObj, opts)

    ddl_file = open('{0}.{1}.DDL.sql'.format(handle, version), 'w')
    
    ddl_file.write("-- dataset --\n")
    ddl_file.write("""INSERT INTO dataset VALUES ('{0}','{1}','{2}','{3}','f');\n""".format(
            handle,
            opts.dataset_description(gseObj),
            opts.dataset_microarray_description(gseObj),
            opts.dataset_pubmed_id(gseObj)))

    ddl_file.write("-- sample --\n")
    all_samples = list(gseObj.metadata.samples)
    for tup in list(gseObj._df.columns):
        samp = gseObj.metadata[tup[sampleLevel]]
        ddl_file.write(
            """INSERT INTO sample VALUES ('{0}', '{1}', '{2}', '{3}', '{4}', '{5}', {6}, '{7}', {8}, '{9}', '{10}', '{11}');\n""".format(
                tup[sampleLevel],
                tup[ctLevel],
                handle,
                opts.sample_description(samp),
                opts.sample_surface_markers(samp),
                opts.sample_notes(samp),
                opts.sample_tissue_id(samp),
                opts.sample_cell_lineage(samp),
                opts.sample_lineage_score(samp),
                opts.sample_old_sample_id(samp),
                opts.sample_cmyk_colour(samp),
                opts.sample_excluded(samp))
            )

    ddl_file.close()
              
    
def main():
    config = Configurator(use_msg="usage: %prog [options] [pickled_GSESeries_file]",
                          config_files=('--guide-config',))

    config.add_option("--input", "-i", action='store', type='string', default='',
                      help="Input file containing the pickled GEOSeries object, created with gse")

    config.add_option("--output", "-o", action='store', type='string', default='',
                      help="Output file in TSV format.")

    config.add_option("--group-by", "-g", action='store', type='string', default='1',
                      help="group columns at the specified index level")

    config.add_option('--handle', '-H', action='store', type='string', default='',
                       help='name of dataset to use in naming the output files, and in the DDL for guide metadata')

    config.add_option('--template', '-t', action='store_true', default=False,
                       help='prints out a template for a configuration file.')

    config.add_option('--version', action='store', type='string', default='',
                       help='name of dataset to use in naming the output files, and in the DDL for guide metadata')

    config.add_option('--verbose', '-v', action='store_true', help='turn on verbose logging', default=False)
    config.add_option('--debug', '-d', default='WARN', help='debug level (DEBUG, INFO, [WARN], ERROR, CRITICAL, FATAL)')

    # Add config file params:
    configure(config)

    opts, args = config()

    log.setLevel(log_levels.get(opts.debug[:3].upper(), logging.WARN))

    log.debug('configuration processed:  opts={0}, args={1}'.format(opts, args))

    # Print a template?
    if opts.template:
        if opts.handle:
            print default_cfg.replace('go.metadata.geo_accession', "'{0}'".format(opts.handle))
        else:
            print default_cfg
        sys.exit(0)

    # Open and read in the series matrix file
    # Pickle and save the resulting object.
    if opts.input != '':
        gmd = cPickle.load(opts.input)

    elif len(args) == 0 :
        config.print_help()
        sys.exit(1)

    elif args[0] == '-':
        gmd = cPickle.load(sys.stdin)

    else:
        gmd = cPickle.load(open(args[0]))

    # Figure out which column index level will be used for "celltype" grouping.
    try:
        lev = int(opts.group_by)
    except:
        lev = opts.group_by
            
    if lev not in gmd.column_index_levels and lev not in range(len(gmd.column_index_levels)):
        raise ValueError('Invalid column index level specified: "{0}"'.format(lev))

    # Emit the pickled matricks files
    createMatricksPickles(gmd, opts, ctLevel=lev)
    createDDL(gmd, opts, ctLevel=lev)



if __name__ == '__main__':  main()
