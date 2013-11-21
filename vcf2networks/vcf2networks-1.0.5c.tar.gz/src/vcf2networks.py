#!/usr/bin/env python
"""
This script takes as input a VCF file, and generates a report of the Genotype Network properties from it.


"""
#import get_gene_coords
import binary_to_network
import filteredvcf_to_binary
import logging
import argparse
import os
import random
#import numpy
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
    parser = argparse.ArgumentParser(#            description=__doc__,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="vcf2networks")
#    config_group = argparse.OptionGroup(parser, "Configuration options. Required")
    config_group = parser.add_argument_group("Configuration options. Required")
    config_group.add_argument('-v', '-g', '--vcf', '--genotypes', dest='vcf_file', 
            help='VCF file to be analyzed. Genotypes must be sorted by position, and belong to the same chromosome. Only Single Nucleotide Polimorphisms, and diploid individuals, are supported. Required.', 
            default=False)
    config_group.add_argument('-i', '--individuals_file', '--individuals', dest='individuals_file', 
            help='File containing the classification of individuals into populations. This must be a tab-separated file, in which the first column is the individual ID, the second is the population, the third is the continental group (or other classification), and the other columns contain classification in phenotypes, one per column. This can also defined in the parameters file (--config). Required.', 
            default="")
    config_group.add_argument('-c', '--config', '--params', dest='params_file', 
            help='File containing many parameters of the analysis. In particular, the list of network properties that will be included in the output report. Required.', 
            default=False)
    config_group.add_argument('-p', '--property', '--phenotype', dest='phenotype', 
            help='Phenotype column used to define the Genotype Networks (e.g. population, disease status, eye color, etc..). When this option is defined, the output will consist of one line for the global population, plus one line for each Genotype Network built using only individuals having the same phenotype.', 
            default="continent")
    config_group.add_argument('-o', '--report_type', dest='report_type', 
#            help='Type of report to produce.  \nPossible values: "interpop_comparison", "values_by_window", "values_by_node", "individuals", and "individuals_line".',
#            choices=("values_by_window", "values_by_node", "interpop_comparison", "individuals", "individuals_line"),
            help='Type of report to produce. "values_by_window" produces one line per each network, giving the average and the maximum of each property (see the configuration file). "values_by_node" produces one line per each node in the network (this will be a very long output). "individuals_line" will print details of the individuals used in the network (this output type is useful when subsampling individuals, combined with the --random_seed option).',
            choices=("values_by_window", "values_by_node", "individuals_line", "individuals"),
            default="values_by_window")
#    parser.add_option_group(config_group)

    network_definition_group = parser.add_argument_group("Network Definition options")
    network_definition_group.add_argument('-n', '-d', '--distance', dest='distance', type=int,
            help='Distance between nodes in the network. Two nodes will be considered as neighbors if they have at least _distance_ number of differences.',
            default=1)
    network_definition_group.add_argument('-w', '--windows_size', '--windows', dest='windows_size', type=int,
            help='Split the region in non-overlapping windows of a given size. If not provided, only a single value for all the genotypes in the VCF file will be provided.', 
            default=0)
    network_definition_group.add_argument('-l', '--overlapping', '--overlapping_windows', dest='overlapping', action='store_true',
            help='Should sliding windows be overlapping? If True, each window will start from the second base of the previous window.',
            default=False)
    network_definition_group.add_argument('-s', '--sample', '--n_haplotypes', '--n_datapoints', dest='n_individuals', type=int,
            help='Sample only this number of individuals. The output will contain an additional line for the global population after subsampling (global_sub), and all the networks will be built using only this fixed number of individuals chosen at random. See also the --replicates and --random_seed options. Also, note that n_individuals = n_haplotypes/2.',
             # NOTE: this var is called n_individuals, although it actually measures n_haplotypes
            default=0)
    network_definition_group.add_argument('-r', '--replicates', '--number_subsampling', dest='n_subsampling', type=int,
            help='How many times to resample individuals (when the --sample option is given).', 
            default=1)
    network_definition_group.add_argument('--random_seed', dest='random_seed', type=int,
            help='Random seed, for sampling individuals. If 0, a random number is used.',
            default=0)
#    parser.add_option_group(network_definition_group)

#    performances_group = argparse.OptionGroup(parser, "Options to save/read networks to files")
#    performances_group.add_argument('--hdf5', '--h5',
#            help='Use HDF5 internal storage. More memory efficient, but requires the h5py library to be installed.',
#            dest='use_hdf5', action='store_true', default=False)
#    parser.add_option_group(performances_group)
#    notimplemented_group = argparse.OptionGroup(parser, "Options not implemented yet")
#    notimplemented_group.add_argument('--parallelize', dest='parallelize', action='store_true', 
#            help='use multiple processors for generating the report',
#            default=False)
#    parser.add_option_group(notimplemented_group)
    parser.add_argument('-u', '--no-debug', dest='debug', action='store_false', 
            help="disable debugging messages, which are enabled by default", default=False)
    options = parser.parse_args()
    
#    if options.parallelize is True:
#        raise NotImplementedError("parallelization wasn't working correctly, so I removed the code for it.")
    if options.report_type in ("interpop_comparison", ):
        raise NotImplementedError("interpop comparison report not implemented yet")
    if options.debug is True:
#        logging.basicConfig(level=logging.DEBUG, filename='logs/network_report.log')
        logging.basicConfig(level=logging.DEBUG)

    if (options.vcf_file is False):
#        parser.print_help()
        parser.error('\n\n\t\tno VCF file provided (check the --vcf option).\n\nPlease use vcf2networks --help to get usage information')
    try:
        if os.stat(options.vcf_file).st_size == 0:
            parser.error("file {0} is empty".format(options.vcf_file))
    except:
        parser.print_help()
        parser.error("Can not open genotypes file {0}".format(options.vcf_file))

    return (options)

def generate_report_windows(options, binary_file, report_type='csv_report'):
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

        * values_by_window report
        * values_by_node report
        * interpop_comparison report

    ------------------------
    values_by_window report 

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
#    genes = get_gene_coords.read_genes_file(options.options.vcf_file)[1]
    individuals_dict = binary_to_network.parse_individuals_file(options.individuals_file)

#    params_file = yaml.load(open(options.params_file, 'r'))
#    pops = params_file['network_phenotypes']['populations']
    report_fields = []
    if report_type == 'values_by_window':
        report_fields.extend(options.params['networkproperties_report_fields'])
        report_fields.append('window')
        report_fields.append('whole_gene_nsnps')
    elif report_type == 'values_by_node':
        report_fields.extend(['genotype', 'name', 'window', 'whole_gene_nsnps'])
        report_fields.extend(options.params["allvalues_report_fields"])
    report_fields.insert(1, options.phenotype)

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

#    if options.n_individuals > 1:
#        pops.insert(0, "global_sub")
    for subsample_id in range(options.n_subsampling):
        random_seed += 1  #TODO: this is the code that breaks the subsampling 
        binary_to_network.print_report_and_subgraphs(binary_file, "gene", individuals_dict, 
                report_type, report_fields, options, random_seed=random_seed, phenotype=options.phenotype)
        random_seed = original_random_seed



def main():
    options = get_options()
#    if options.windows_size != 0:
#    (genotypes_lines, unphased_genotypes, snp_ids, snp_annotations ) = filteredvcf_to_binary.read_genotypes_vcf(options.vcf_file)

    # Get the name of the individuals_file
    if options.params_file is False:
        options.params = {
                'networkproperties_report_fields': ['file_prefix', 'n_snps', 'chromosome', 'n_datapoints', 'n_components', 'av_degree', 'av_path_length'],
                'individuals_file': 'data/individuals/individuals_annotations.txt'}
    else:
        options.params = yaml.load(open(options.params_file, 'r'))

#    print options.params_file
    if options.individuals_file == "":
        if options.params.has_key('individuals_annotations'):
            options.individuals_file = options.params['individuals_annotations']
        else:
            argparse.error("no individuals file (--individuals_file option) provided")
    if not os.path.isfile(options.individuals_file): argparse.error('Invalid individuals file. Please specify one with the -i option, or in the parameters file')
#    try: with open(options.vcf_file) as f: pass except IOError as e: 'Invalid VCF file file. Please specify one with the -i option, or in the parameters file'

    # Generate a temporary file containing the genotypes.
    options.use_hdf5 = False
    binary_file_contents = filteredvcf_to_binary.print_binary_file(options.vcf_file, options)
    import tempfile
    binary_file = tempfile.TemporaryFile()
    binary_file.write(binary_file_contents)
    binary_file.seek(0)
#    print genotypes_lines
#    print snp_annotations
    generate_report_windows(options, binary_file, options.report_type)

    options_line = "vcf_file: {0}\tparams_file: {1}\twindow_size: {2}\toverlapping: {3}\tn_individuals: {4}".format(options.vcf_file, options.params_file, options.windows_size, options.overlapping, options.n_individuals)
    logging.debug("network report generated correctly - " + options_line)
#    else:
#        generate_report_old(options)

if __name__ == '__main__':
    main()
