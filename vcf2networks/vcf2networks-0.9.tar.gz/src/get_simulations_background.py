#!/usr/bin/env python
"""
Parse all simulations, and get a file with distributions of values.
"""
import glob
import binary_to_network 
import yaml
import gzip
import re
import optparse
import random
from GenotypeNetwork import GenotypeNetworkInitError
import numpy
import warnings
import StringIO
import os

def get_options():
    parser = optparse.OptionParser(
			usage="python %prog -f genes_file.genes", 
            description=__doc__)
    config_group = optparse.OptionGroup(parser, 
			"Configuration options. Required")
    config_group.add_option(
			'-f', '-s', '--simulations_folder', dest='simulations_folder', 
            help='File containing the list of genes to be analyzed. Required. Default: %default', 
			default='./data/simulations/binary/globalpops')
    config_group.add_option('-p', '--params', dest='params_file', 
            help='File containing the parameters of the analysis. In particular, the fields to be included in the report. Required. Default: %default', 
            default="params/default.yaml")
    config_group.add_option('--background_type', '--report_type', '-b', '-t', 
			dest='report_type', 
            help='Type of report to produce.\nPossible values: "interpop_comparison", "values_by_gene", "values_by_node", "individuals", and "individuals_line". Default: %default',
            choices=("values_by_gene", "values_by_node", "interpop_comparison",
					"individuals", "individuals_line"),
            default="values_by_gene")
    parser.add_option_group(config_group)
    network_definition_group = optparse.OptionGroup(parser, 
			"Network Definition options")
    network_definition_group.add_option('-n', '-d', '--distance', 
			dest='distance', type='int',
            help='Distance between nodes in the network. Two nodes will be considered being neighbors if they have at least _distance_ number of differences. Default: %defaul',
            default=1)
    network_definition_group.add_option('-w', '--windows_size', '--windows', 
			dest='windows_size', type='int',
            help='Size of window to use. If 0, all data will be included. Default: %default', 
            default=11)
    network_definition_group.add_option('-i', '--individuals', '--number_individuals', 
			dest='n_individuals', type='int',
            help='Number of individuals to be included. If 0, all the individuals are used. Default: %default', 
            default=0)
    network_definition_group.add_option('--random_seed', dest='random_seed', type='int',
            help='seed for random sampling when --individuals is defined. If 0, then a random seed is used. Default: %default', 
            default=0)
    network_definition_group.add_option('-r', '--number_subsampling', dest='n_subsampling', type='int',
            help='How many times to resample individuals, if the -i option is not 0. Default: %default', 
            default=1)
    network_definition_group.add_option('-g', '--global', dest='global_pop', action='store_true', 
            help="Calculate network properties for a global population as well.", default=False)
    parser.add_option_group(network_definition_group)
    notimplemented_group = optparse.OptionGroup(parser, 
			"Options not implemented yet")
    notimplemented_group.add_option('--hdf5', dest='use_hdf5', action='store_true', 
            help='Use HDF5 file instead of binary',
            default=False)
    notimplemented_group.add_option('--parallelize', dest='parallelize', 
			action='store_true',
            help='use multiple processors for generating the report',
            default=False)
    parser.add_option_group(notimplemented_group)
    parser.add_option('-u', '--no-debug', dest='debug', action='store_false', 
            help="disable debugging messages, which are enabled by default", 
			default=True)
    (options, args) = parser.parse_args()
    
    if options.parallelize is True:
        raise NotImplementedError("parallelization wasn't working correctly, so I removed the code for it.")
    if options.report_type in ("interpop_comparison", ):
        raise NotImplementedError("interpop comparison report not implemented yet")
    if options.use_hdf5 is True:
        raise NotImplementedError("no support for HDF5 in simulations yet")
    if options.windows_size == 0:
        raise NotImplementedError("windows_size == 0 not implemented yet")
    if options.debug is True:
        logging.basicConfig(level=logging.DEBUG, filename='logs/network_report.log')
    
    options.simulations_folder = options.simulations_folder + '/'

    return (options)

class SimulationsParserError(Exception):
    """
    Generic error raise when something goes wrong while parsing sims.
    """
    pass

def get_simulations_background(simulations_folder, 
        windows_size = 11, 
        params_file = 'params/default.yaml', 
        report_type = 'values_by_gene', 
        distance = 1,
        n_individuals = 0,
        n_subsampling = 1,
        random_seed = False):
    """
    Generate a file containing the distribution of values for network 
	 properties in the simulations.

    For each simulation, parse the corresponding file and calculate 
	 many network properties, thanks to the csv_report function.
    Then, print these properties on a new line, and move to the next 
	 simulation.
    """
    continent_map = {
        '1': 'EUR',
        '2': 'ASN',
        '3': 'AFR',
        '0': 'glob',
        'pop1': 'EUR',
        'pop2': 'ASN',
        'pop3': 'AFR',
        'pop0': 'glob'
        }

    if random_seed == 0:
        random_seed = random.random()

    params_file = yaml.load(open(params_file, 'r'))
    report_fields = []
    if report_type == 'values_by_gene':
        report_fields.extend(params_file['networkproperties_report_fields'])
        report_fields.extend(["window", "whole_gene_nsnps"])
    elif report_type == 'values_by_node':
        report_fields.extend(["genotype", "name", "window", "whole_gene_nsnps"])
        report_fields.extend(params_file['allvalues_report_fields'])

    simulations_basedir = simulations_folder

    networks = {}
    header = ' '.join(report_fields) 
    output_background = header
    print header
    options.overlapping = True
    options.use_hdf5 = False

    allsimulations = sorted(glob.glob(simulations_basedir + '*binary.gz'))
    original_random_seed = random_seed

    for simfile_name in allsimulations:
        try:
            
            if os.path.exists(simfile_name) is False:
                break
            simfile = open(simfile_name, 'r')

            # check if file is gzipped
            if simfile.read(2) == "\x1f\x8b":
                simfile = gzip.open(simfile_name, 'r')
            else:
                simfile.seek(0)
            if n_individuals > 0:
                random_seed = original_random_seed
                for subsample in xrange(n_subsampling):
                    random_seed += 1 
#                    print
#                    print random_seed
                    binary_to_network.print_report_and_subgraphs(simfile, 
							"neutral_sim", individuals_dict=False, 
                            pops=["global_sub", "EUR", "ASN", "AFR"], 
							report_type=options.report_type, 
							report_fields=report_fields, 
                            options=options, central_window_only=True,
                            n_individuals=n_individuals, random_seed=random_seed)
            else:
                binary_to_network.print_report_and_subgraphs(simfile, 
						"neutral_sim", individuals_dict=False, 
                        pops=["EUR", "ASN", "AFR"], 
						report_type=options.report_type,
						report_fields=report_fields,
                        options=options, central_window_only=True,
                        n_individuals=n_individuals, random_seed=random_seed)

        except GenotypeNetworkInitError:
            pass
#        print
    return output_background


if __name__ == '__main__':
    import logging
    import doctest
    logging.basicConfig(level=logging.DEBUG)
    options = get_options()
    get_simulations_background(
                    simulations_folder = options.simulations_folder,
                    windows_size = options.windows_size, 
                    params_file = options.params_file, 
                    report_type = options.report_type, 
                    distance=options.distance,
                    n_individuals=options.n_individuals,
                    n_subsampling=options.n_subsampling,
                    random_seed = options.random_seed)


