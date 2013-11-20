#!/usr/bin/env python
"""
This script will call binary_to_network.py on all the genes of a pathway, and 
create different types of reports for all the properties (see the option 
--report_type for a list of all possible report types).

It requires a single argument, a genes file containing all the genes to be 
included in the analysis. 
This is the same file used in get_gene_coords.py, and is also described 
in the main README.rst of this repository.

Morever, this script will assume that files containing the genotypes in 
binary format (produced by filteredvcf_to_binary.py) are stored in the 
data/binary directory. 
If one of these files is missing or empty, a warning message will be 
sent to logs/generate_network_report.txt

"""
import get_gene_coords
import binary_to_network
import logging
import optparse
import os
import random
import numpy
try:
    from GenotypeNetwork import GenotypeNetworkInitError
    import GenotypeNetwork
except ImportError:
    from src.GenotypeNetwork import GenotypeNetworkInitError as GenotypeNetworkInitError
    from src.GenotypeNetwork import GenotypeNetwork
import yaml
import re
#import gc
#import multiprocessing

def get_options():
    parser = optparse.OptionParser(usage="python %prog -f genes_file.genes", 
            description=__doc__)
    config_group = optparse.OptionGroup(parser, "Configuration options. Required")
    config_group.add_option('-f', '-g', '-v', '--genes', dest='genes_file', 
            help='File containing the list of genes to be analyzed. Required. Default: %default. ', default=False)
    config_group.add_option('-p', '--params', dest='params_file', 
            help='File containing the parameters of the analysis. In particular, the fields to be included in the report. Required. Default: %default', 
            default="params/default.yaml")
    config_group.add_option('--report_type', '-t', '-r', dest='report_type', 
            help='Type of report to produce.  \nPossible values: "interpop_comparison", "values_by_gene", "values_by_node", "individuals", and "individuals_line". Default: %default',
            choices=("values_by_gene", "values_by_node", "interpop_comparison", "individuals", "individuals_line"),
            default="values_by_gene")
    parser.add_option_group(config_group)
    network_definition_group = optparse.OptionGroup(parser, "Network Definition options")
    network_definition_group.add_option('-n', '-d', '--distance', dest='distance', type='int',
            help='Distance between nodes in the network. Two nodes will be considered being neighbors if they have at least _distance_ number of differences. Default: %default',
            default=1)
    network_definition_group.add_option('-w', '--windows_size', '--windows', dest='windows_size', type='int',
            help='Split the gene in non-overlapping windows of a given size. If not provided, windows approach won\'t be used. Default: %default', 
            default=0)
    network_definition_group.add_option('-i', '--individuals', '--number_individuals', dest='n_individuals', type='int',
            help='Number of individuals to use. If it is less than the actual number of samples, only a randomly chosen subset of these is used. This value is applied only to the population networks, not to the global one. Also, note that n_individuals = n_haplotypes/2. Default: %default',
            default=0)
    network_definition_group.add_option('-l', '--overlapping', '--overlapping_windows', dest='overlapping', action='store_true',
            help='Should sliding windows be overlapping? If True, each window will start from the second base of the previous window. Default: %default',
            default=False)
    network_definition_group.add_option('--random_seed', dest='random_seed', type='int',
            help='Random seed, for sampling individuals. If 0, a random number is used. Default: %default',
            default=0)
    network_definition_group.add_option('-s', '--number_subsampling', dest='n_subsampling', type='int',
            help='How many times to resample individuals, if the -i option is not 0. Default: %default', 
            default=1)
    parser.add_option_group(network_definition_group)
    performances_group = optparse.OptionGroup(parser, "Options to save/read files from graphml and pickle")
    performances_group.add_option('--write_pickle', dest='write_pickle', action='store_true',
            help='Write networks to pickle files, to the data/pickle folder', 
            default=False)
    performances_group.add_option('--write_graphml', dest='write_graphml', action='store_true',
            help='Write networks to graphml files, to the data/graphml folder', 
            default=False)
    performances_group.add_option('--overwrite_existing', dest='overwrite_existing', action='store_true',
            help='Used in combination with --write_graphml and --write_pickle, overwrite files if they already exist',
            default=False)
    performances_group.add_option('--read_graphml_if_possible', dest='read_graphml_if_possible', action='store_true',
            help='Attempt to read networks from graphml files, if they exists. Otherwise, generate new network', 
            default=False)
    performances_group.add_option('--data_basedir', dest='data_basedir', type='str',
            help='Path to the folder where graphmlfiles and pickle files will be stored or loaded from. Example: ./data/',
            default='./data/')
    performances_group.add_option('--hdf5', '--h5',
            help='Use HDF5 internal storage. More memory efficient, but requires the h5py library to be installed.',
            dest='use_hdf5', action='store_true', default=False)
    parser.add_option_group(performances_group)
    notimplemented_group = optparse.OptionGroup(parser, "Options not implemented yet")
    notimplemented_group.add_option('--parallelize', dest='parallelize', action='store_true', 
            help='use multiple processors for generating the report',
            default=False)
    parser.add_option_group(notimplemented_group)
    parser.add_option('-u', '--no-debug', dest='debug', action='store_false', 
            help="disable debugging messages, which are enabled by default", default=True)
    (options, args) = parser.parse_args()
    
    if options.parallelize is True:
        raise NotImplementedError("parallelization wasn't working correctly, so I removed the code for it.")
    if options.report_type in ("interpop_comparison", ):
        raise NotImplementedError("interpop comparison report not implemented yet")
    if options.debug is True:
        logging.basicConfig(level=logging.DEBUG)

    if (options.genes_file is False) and (len(args) == 0):
        parser.print_help()
        parser.error('generate_network_report.py error: no genes file provided')
    try:
        genes_file_path = ''
        if options.genes_file is not False:
            genes_file_path = options.genes_file
        elif args != '':
            network_from_graphml = args[0]
        if os.stat(genes_file_path).st_size == 0:
            parser.error("file {0} is empty".format(genes_file_path))
    except:
        print __doc__
        parser.error("Can not open genotypes file {0}".format(options.genes_file))
    options.genes_file_path = genes_file_path

    return (options)

def generate_report_windows(options, report_type='csv_report'):
    """
    Parse a file containing binary genotypes, generate a Genotype Network for each population, and write a report showing a resume of the network properties.

    +++++++++++++++++
    Parameters
    +++++++++++++++++

    - options: see the documentation for this script (--help)
    - columns included in the report file: these are defined in the params file.

    ++++++++++++++++++++++
    Example output report:
    ++++++++++++++++++++++

    There are three possible output report:

        * values_by_gene report
        * values_by_node report
        * interpop_comparison report

    ------------------------
    values_by_gene report 

    This report shows one line per every window/gene.
     
    ::

        gene continent distance_definition n_snps n_datapoints av_datapoints_per_node n_vertices n_edges n_components av_path_length diameter av_degree window whole_gene_nsnps
        ALG3 glob 1 30 2184 42.8235 51 50 6 3.7783 8 1.9608 8 0.0319 window_0 76
        ALG3 glob 1 30 2184 59.027 37 31 9 3.2544 7 1.6757 12 0.0517 window_1 76
        ALG3 AFR 1 30 492 13.6667 36 31 6 2.9438 6 1.7222 5 window_0 76
        ALG3 AFR 1 30 492 21.3913 23 15 8 3.1481 7 1.3043 5 window_1 76
        ALG3 ASN 1 30 572 63.5556 9 4 5 1.2 2 0.8889 2 window_0 76


    ------------------------
    values_by_node report 

    This report shows one line per every window/gene.
     
    ::
        
        genotype    degree  closeness
        01000       2       0.6
        00000       1       0.3
        01001       1       0.3 


    ------------------------
    interpop_comparison

    Not implemented yet
     
    """
    random_seed = options.random_seed
    original_random_seed = random_seed
    if random_seed is False:
        random_seed = random.random()
    genes = get_gene_coords.read_genes_file(options.genes_file_path)[1]
    individuals_dict = binary_to_network.parse_individuals_file()

    params_file = yaml.load(open(options.params_file, 'r'))
    pops = params_file['data']['populations']
    report_fields = []
    if report_type == 'values_by_gene':
        report_fields.extend(params_file['networkproperties_report_fields'])
        report_fields.append('window')
        report_fields.append('whole_gene_nsnps')
    elif report_type == 'values_by_node':
        report_fields.extend(['genotype', 'name', 'window', 'whole_gene_nsnps'])
        report_fields.extend(params_file["allvalues_report_fields"])

    if options.use_hdf5 is True:
        binaryfile_basepath = options.data_basedir + '/hdf5/{0}_genotypes.hdf5'
    else:
        binaryfile_basepath = options.data_basedir + '/binary_genotypes/{0}.binary'
#    graphmlfile_basepath = options.data_basedir + '/graphml/{}_{}_distance{}.graphml'
#    picklefile_basepath = options.data_basedir + '/pickles/{}_{}_distance{}.pickle'
#    networks = {}
    header = ' '.join(report_fields) 

    print header
#    report_output = header + '\n'
    windows_size = options.windows_size
    if options.overlapping is True:
        step = 1
    else:
        step = windows_size

    if options.n_individuals > 1:
        pops.insert(0, "global_sub")
    for gene in genes:
#        logging.debug("generated network report for gene {0}".format(gene))
        if gene not in ('gene',):
            skip_gene = False
            allpops_binaryfilepath = binaryfile_basepath.format(gene)
            try:
                allpops_binaryfile = open(allpops_binaryfilepath, 'r')
            except IOError:
                skip_gene = True
                logging.warn("The Binary File for {0} is not found.".format(allpops_binaryfilepath))
#                continue
            if skip_gene is False:
                for subsample_id in range(options.n_subsampling):
                    random_seed += 1  #TODO: this is the code that breaks the subsampling 
                    binary_to_network.print_report_and_subgraphs(allpops_binaryfile, gene, individuals_dict, 
                            pops, report_type, report_fields, options, random_seed=random_seed)
        random_seed = original_random_seed
#        logging.debug("gene {0} completed".format(gene))
#   return report_output


def read_graphml(input_graphmlfile, read_graphml_if_possible, binaryfile, individuals_dict, distance, gene):
    current_network = None
    if read_graphml_if_possible is True:    #TODO: convert back to GenotypeNetwork object
        logging.info("Trying to read " + input_graphmlfile)
        try:
            current_network = GenotypeNetwork.network_from_graphml(input_graphmlfile)
        except:
            logging.warn("could not read file from graphml, " + input_graphmlfile)
    if current_network is None:
        logging.info("Generating network from " + binaryfile)
        try:
            current_network = binary_to_network.generate_network(binaryfile, 
                          individuals_dict=individuals_dict, distance=distance)
        except:
            logging.error("Failed reading binary {0} file for {1}".format(binaryfile, gene))
            current_network = False
#    if current_network is None:
#        continue
    return current_network
def write_graphml(output_graphmlfile, current_network, overwrite_existing):
    """Write a network to a graphmlfile, if it doesn't exist already or overwrite_existing is True"""
    force_graphml_write = False
    if not os.path.exists(output_graphmlfile):
        force_graphml_write = True
    elif (overwrite_existing is True) and (os.stat(output_graphmlfile).st_size > 0):
        force_graphml_write = True
    if force_graphml_write is True:
        logging.info("wrote graphml to " + output_graphmlfile)
        try:
            current_network.write_graphml(output_graphmlfile)
        except TypeError:
            logging.warn("Error saving {0} file".format(output_graphmlfile))
    else:
        logging.info("graphml file {0} not written, because it already exists and the --overwrite option is not True".format(output_graphmlfile))

def write_pickle(output_picklefile, current_network, overwrite_existing):
    """Write a network to a picklefile, if it doesn't exist already or overwrite_existing is True"""
    force_pickle_write = False
    if not os.path.exists(output_picklefile):
        force_pickle_write = True
    elif (overwrite_existing is True) and (os.stat(output_picklefile).st_size > 0):
        force_pickle_write = True
    if force_pickle_write is True:
        logging.info("wrote pickle to " + output_picklefile)
        current_network.write_pickle(output_picklefile)
    else:
        logging.info("picklefile {0} not written, because it already exists and the --overwrite option is not True".format(output_picklefile))


if __name__ == '__main__':
    options = get_options()
#    if options.windows_size != 0:
    generate_report_windows(options, options.report_type)
    options_line = "genes_file: {0}\tparams_file: {1}\twindow_size: {2}\toverlapping: {3}\tn_individuals: {4}".format(options.genes_file_path, options.params_file, options.windows_size, options.overlapping, options.n_individuals)
    logging.debug("network report generated correctly - " + options_line)
#    else:
#        generate_report_old(options)

