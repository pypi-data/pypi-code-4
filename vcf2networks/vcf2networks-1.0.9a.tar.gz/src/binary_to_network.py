#!/usr/bin/env python
"""
Parse a file in .binary format and produce a Genotype Network.

When invoked from the command line, it also prints a linear report of network properties.

"""
import logging
import optparse
import os
from custom_exceptions import *
from filteredvcf_to_binary import parse_individuals_file
#import cPickle
import operator 
import re
import random
#import gc
import numpy
from GenotypeNetwork import GenotypeNetwork


def get_options():
    """Get command line arguments
    """
    parser = optparse.OptionParser(usage="python %prog -f genotypes.binary", 
            description=__doc__)
    parser.add_option('-f', '-g', '-v', '--genotypes', dest='genotypes_file', 
            help='File containing the genotypes in binary format, produced \
by src/parse_genotypes.py', default=False)
    parser.add_option('-u', '--no-debug', dest='debug', action='store_false', 
            default=True)
    parser.add_option('-n', '-d', '--distance', dest='distance', type='int',
            help='Distance between nodes in the network. Two nodes will be \
considered being neighbors if they have at least _distance_ \
number of differences',
            default=1)
    parser.add_option('-s', '--upstream', dest='upstream', type='int',
            help='upstream position, to extract a subset of SNPs. \
The SNP at upstream position is included.',
            default=None)
    parser.add_option('-e', '--downstream', dest='downstream', type='int',
            help='downstream position, to extract a subset of SNPs',
            default=None)
    parser.add_option('-i', '--n_individuals', dest='n_individuals', type='int',
            help='Number of individuals to use. If 0, all individuals are used',
            default=0)
    parser.add_option('--hdf5', '--h5',
            help='Use HDF5 internal storage. More memory efficient, but requires the h5py library to be installed.',
            dest='use_hdf5', action='store_true', default=False)
    (options, args) = parser.parse_args()
    
    if options.debug is True:
        logging.basicConfig(level=logging.DEBUG, 
                filename='logs/generate_networks.log')

    if (options.genotypes_file is False) and (len(args) == 0):
        parser.print_help()
        parser.error('generate_networks.py error: no genotypes file provided')
    try:
        binary_file_path = ''
        if options.genotypes_file is not False:
            binary_file_path = options.genotypes_file
        elif args != '':
            binary_file_path = args[0]
        if os.stat(binary_file_path).st_size == 0:
            parser.error("file {0} is empty".format(binary_file_path))
    except:
        print __doc__
        parser.error("Can not open genotypes file {0}".format(options.genotype_file))

    if options.upstream < options.downstream:
        parser.error("Window Start can not be higher than Window End ({0}, {1})".format(options.upstream, options.downstream))

    if options.use_hdf5 is True:
        import h5py

    return (binary_file_path, options)

def parse_hdf5_file(hdf5_file, individuals_dict=None):
    """
    Parse a HDF5 file, and return a numpy matrix
    """
#    raise NotImplemented
    import h5py 
    logging.debug( hdf5_file)
    import os
    logging.debug(os.getcwd())
    import glob
#    logging.debug(glob.glob(hdf5_file))

    if isinstance(hdf5_file, str):      #TODO: this doesn't seem to work
        # hdf5_file is a path to a file. Open it.
        hdf5_file = h5py.File(hdf5_file, 'r')

    if hasattr(hdf5_file, "name"):
        hdf5file_path = hdf5_file.name
        # TODO: avoid closing/reopening of HDF5 files
        hdf5_file.close()
        hdf5_file = h5py.File(hdf5file_path, 'r')
#        gene_name = hdf5file_path.split('/')[-1].split('.',1)[0]
    else:
        hdf5file_path = 'stringIO object'
#        gene_name = 'unknown_gene'
#    print hdf5_file.values()
    gene_name = hdf5_file['indv_annotations'][0,0]
    individuals = []
    filteredout_genotypes = set([])
    #TODO: make sure that this works correctly when individuals_dict is passed as a parameter to this function
#    if individuals_dict is None or individuals_dict is False:   
    indv_annotations = hdf5_file['indv_annotations']
    for indv in indv_annotations:
        individual_key = indv[1].replace("_1", "").replace("_2", "").replace("_a", "").replace("_b", "")
        individuals.append(indv[1])
        individuals_dict.setdefault(individual_key, {})
        individuals_dict[individual_key]['subpop'] = indv[2]
#            continent = indv[3]
        individuals_dict[individual_key]['pop'] = indv[3]
        individuals_dict[individual_key]['continent'] = indv[3]
        individuals_dict[individual_key].setdefault('techniques', '')
#            sex = indv[4]
        individuals_dict[individual_key]['sex'] = 'X'
#    else:
#        individuals = individuals_dict.keys()

    all_genotypes = hdf5_file['genotype_line']
    if len(all_genotypes) == 0:
        raise GenotypeNetworkInitError("No genotypes in {0}".format(hdf5file_path))
#    print individuals
#    print individuals_dict.items()[0:2]

    # FILTER genotypes that are not 0 or 1 
    # NOTE: FILTERING of wrong genotypes is not implemented yet. This is fine
    # because none of the files should contain wrong genotypes.
    filteredout_genotypes = set([])
    for snp_column in range(all_genotypes.len()):
        if max(all_genotypes[snp_column, :]) > 1:
            filteredout_genotypes.update(snp_column)
            
    if len(filteredout_genotypes) > 0:
        kept = [n for n in range(total_number_snps) if n not in filteredout_genotypes]
        logging.warn("Triallelic SNP found in {0}".format(binaryfile_path))
        raise NotImplemented("filtering of Triallelic SNPs is not implemented yet")
    # MAF FILTER: not implemented at this stage. MAF filters are applied when filtering the VCF file.


    return all_genotypes, individuals, individuals_dict, gene_name


def parse_binary_file(binary_file, individuals_dict=None):
    """
    Parse a binary file, and return a numpy matrix
    """
    if isinstance(binary_file, str):
        # binary_file is a path to a file. Open it.
        binary_file = open(binary_file, 'r')

    if hasattr(binary_file, "name"):
        binaryfile_path = binary_file.name
#        gene_name = binaryfile_path.split('/')[-1].split('.',1)[0]
    else:
        binaryfile_path = 'stringIO object'
#        gene_name = 'unknown_gene'

    all_genotypes = []
    individuals = []
    filteredout_genotypes = set([])
    if individuals_dict is None or individuals_dict is False:
        individuals_dict = {}
    for line in binary_file:
        if not line.strip() == '':
            if not line.startswith('#'):
#                print line
                if not re.match('^\d+$', line):
#               if line.startswith('neutral_sim'):
                    fields = line.split()
                    gene_name = fields[0]
                    individual = fields[1]
                    individual_key = fields[1].replace("_1", "").replace("_2", "").replace("_a", "").replace("_b", "")
                    individuals_dict.setdefault(individual_key, {})
#                    population = fields[2]
                    individuals_dict[individual_key]['subpop'] = fields[2]
#                    continent = fields[3]
                    individuals_dict[individual_key]['pop'] = fields[3]
                    individuals_dict[individual_key]['continent'] = fields[3]
                    individuals_dict[individual_key].setdefault('techniques', '')
#                    sex = fields[4]
                    individuals_dict[individual_key]['sex'] = 'X'
                    genotypes = fields[5:]

#                    print "AAAAAAAA", fields[0:9]
#                    if downstream is not None:
#                        downstream = min(len(genotypes), downstream)
#                    else:
#                        downstream = len(genotypes)
#
                    # TODO: this can be done better using numpy's tools
                    for pos in xrange(len(genotypes)):
                        if genotypes[pos] not in ("0", "1"):
                            filteredout_genotypes.update([pos])

#                    all_genotypes.append(''.join(genotypes[upstream:downstream]))
                    all_genotypes.append(''.join(genotypes))
                    individuals.append(individual)
    if len(all_genotypes) == 0:
        raise GenotypeNetworkInitError("No genotypes in {0}".format(binaryfile_path))
#        continue
    total_number_snps = len(all_genotypes[0])

    # Filter out all SNPs that have at least one genotype different from 0 or 1
    if len(filteredout_genotypes) > 0:
        kept = [n for n in range(total_number_snps) if n not in filteredout_genotypes]
        logging.warn("Triallelic SNP found in {0}".format(binaryfile_path))
        if len(kept) == 0:
            error_message = "No valid genotypes found for {0} after filtering".format(binaryfile_path)
            logging.warn(error_message)
            raise GenotypeNetworkInitError(error_message)
#            continue
        get_notnull_genotypes = operator.itemgetter(*kept)
        logging.debug("removed {0} genotypes out of {1} after filtering for MAF and for wrong genotypes".format(len(filteredout_genotypes), len(all_genotypes[0])))
#        print kept
        all_genotypes = [''.join(get_notnull_genotypes(genotypes)) for genotypes in all_genotypes]
#        print all_genotypes
#    print(filteredout_genotypes)
#    print(len(all_genotypes), all_genotypes[:10])
    return all_genotypes, individuals, individuals_dict, gene_name

#def generate_network(binary_file, individuals_dict=None, distance=1, 
#        upstream=None, downstream=None, n_individuals = 0, random_seed=False,
#        window_size=None, overlapping_windows=None):


def generate_network(all_genotypes, individuals, individuals_dict, gene_name,
        distance = 1, upstream=None, downstream = None, n_individuals = 0, 
        random_seed = False, window_size = None, overlapping_windows = None,
        use_hdf5 = False):
    """
    Given a set of genotypes, generate a genotype network.


    # TODO: update documentation, after splitting the function and adding use_hdf5 option

    ++++++++++
    Parameters
    ++++++++++
    
        binary_file
            binary file object or path (see below for example of format)

        individuals_dict
            file containing individuals and population definitions

        distance
            definition of distance between neighbors in the genotype space
        
        upstream, downstream
            positions to extract only a subset of SNPs from the data. Start position is included.

    +++++++++++++++++++
    Example and doctest
    +++++++++++++++++++

    >>> from StringIO import StringIO
    >>> binary_file = StringIO()
    >>> sample_binary_file = r'''#
    ... # gene  chromosome_id rs1 rs2 rs3 rs4 rs5 rs6 rs7
    ... MOGS HG00096_1 GBR EUR X 0 0 0 1 1 0 0
    ... MOGS HG00096_2 GBR EUR X 0 0 0 1 1 0 0
    ... MOGS HG00097_1 GBR EUR X 0 0 0 0 0 0 0
    ... MOGS HG00097_2 GBR EUR X 0 0 0 0 0 0 0
    ... MOGS HG00099_1 GBR EUR X 0 0 0 0 0 0 1
    ... MOGS HG00099_2 GBR EUR X 0 0 0 0 0 0 1
    ... MOGS HG00100_1 GBR EUR X 0 0 0 0 1 0 0
    ... MOGS HG00100_2 GBR EUR X 0 0 0 0 1 0 0
    ... MOGS HG00101_1 GBR EUR X 1 0 0 0 1 0 0
    ... MOGS HG00101_2 GBR EUR X 1 0 0 0 1 0 0
    ... '''
    >>> binary_file.write(sample_binary_file)
    >>> binary_file.seek(0)
    >>> individuals_dict = parse_individuals_file()
    >>> genotypes, individuals, individuals_dict, gene_name = parse_binary_file(binary_file, individuals_dict)
    >>> network = generate_network(genotypes, individuals, individuals_dict, "MOGS")
    >>> print network.summary() #doctest: +NORMALIZE_WHITESPACE
    5 nodes, 4 edges, undirected
    <BLANKLINE>
    Number of components: 1
    Diameter: 3
    Density: 0.4000
    Average path length: 1.8000
    >>> print network['individuals']
    ['HG00096_1', 'HG00096_2', 'HG00097_1', 'HG00097_2', 'HG00099_1', 'HG00099_2', 'HG00100_1', 'HG00100_2', 'HG00101_1', 'HG00101_2']

    
    """

        
#    print "GENO:", all_genotypes[0:5]
#    print set([len(geno) for geno in all_genotypes])
    if upstream is None:
        upstream = 0
    else:
        upstream = upstream - 1
    if downstream is None:
        downstream = len(all_genotypes[0])
    else:
        downstream = min(downstream, len(all_genotypes[0]))
    if upstream > downstream:
        raise ValueError("Window Start can not be bigger than Window End")

    # SUBSAMPLE NETWORK, if required
    if random_seed is not False:
        random.seed(random_seed)
    if n_individuals > 0:
        if n_individuals < len(all_genotypes):
            all_genotypes = random.sample(all_genotypes, n_individuals)

    chromosome_len = downstream-upstream

    # GENERATE NETWORK
    network = GenotypeNetwork(chromosome_len, name=gene_name)
    if use_hdf5 is True:
        all_genotypes = all_genotypes[:, upstream:downstream]
        all_genotypes = ["".join([str(geno) for geno in indv_genos]) for indv_genos in all_genotypes]
    else:
        all_genotypes = [genotype[upstream:downstream] for genotype in all_genotypes]
#    print gene_name, all_genotypes[0:5]

#    print all_genotypes[0:5]
    network.populate_from_binary_strings_and_individuals(
            genotypes=all_genotypes, distance=distance, 
            individuals=individuals, individuals_dict=individuals_dict)
    return network

def generate_network_wrapper(options):
    """wrapper function to run generate_network in parallel

    """
    binary_file_path = options[0]
    individuals_dict = options[1]
    return generate_network(binary_file_path, individuals_dict)



def print_report_and_subgraphs(allpops_binaryfile, gene, individuals_dict, 
            report_type, report_fields, options, 
            central_window_only=False, random_seed=0, 
            phenotype="continent", 
            pops=False,         # DEPRECATED
            n_individuals=0    # DEPRECATED
            ): 
    """
    Given the path to a binary file, generate a report of network properties 
    of the global graph and of the subpopulations.

    Parameters:
    - allpops_binary_file   -> handler to a .binary file (see filteredvcf_to_binary.py)
    - gene                  -> a label for the gene, region, or window. This will be the name of the network.
    - individuals_dict      -> dictionary containing list of individuals and populations. Recommended to leave it False.
    - pops                  -> populations for which to calculate the subnetwork. 
                                If empty, only the properties of the global network will be calculated. 
                                Recommended: ['EUR', 'ASN', 'AFR'].
    - report_type           -> whether to print a report per every node or per every network.
    - report_fields         -> which fields to include in the report.
    - options               -> misc options, including windows_size, distance_definition, upstream and downstream position...
    - central_window_only   -> If True, only the properties of the central window will be calculated.
    - n_individuals         -> If >0, sample only a subset of individuals for every population.
    - random_seed           -> seed for subsampling individuals randomly.
    - phenotype             -> the phenotype by which splitting individuals in different networks (default: by continent)
    """
#    print allpops_binaryfile.name
    skip_gene = False
    networks = {}
    networks[gene] = {}
    networks[gene]['glob'] = {}

    snp_ids = []
    chromosomes = []
    positions = []
    ref_alleles = []
    n_snps = None
#    report_fields.insert(1, phenotype)
#    print report_fields

    if options.use_hdf5 is False:
        while n_snps is None:
            current_line = allpops_binaryfile.readline()
            if current_line.startswith('#'):
                if current_line.startswith('#SNP IDS:'):
                    snp_ids = current_line.split()[2:]
                if current_line.startswith('#Chromosome:'):
                    chromosomes = current_line.split()[1:]
                if current_line.startswith('#Position:'):
                    positions = [int(p) for p in current_line.split()[1:]]
                if current_line.startswith('#Ref. allele:'):
                    ref_alleles = current_line.split()[2:]
            else:
                snps_str = re.findall("^.*?\s+?([01 ]*)$", current_line)
                if snps_str != []:
                    n_snps = len(snps_str[0].split())
            if current_line == '': # if current_line is empty, it means that we reached the downstream of the file
                logging.warn("The Binary File for {0} is not valid".format(allpops_binaryfile.name))
                skip_gene = True
                break
        allpops_binaryfile.seek(0)
    elif options.use_hdf5 is True: # TODO: what happens if the HDF5 file doesn't contain snp_annotations?
        import h5py
#        print allpops_binaryfile.name
        try:
            hdf5_file = h5py.File(allpops_binaryfile.name, 'r')
        except:
            logging.warn("The HDF5 file for {0} is not found or could not be opened".format(allpops_binaryfile.name))
            return
        snp_annotations = hdf5_file['snp_annotations']
        snp_ids = snp_annotations[:, 0]
        chromosomes = snp_annotations[:, 1]
        positions = [int(p) for p in snp_annotations[:, 2]]
#        print positions[0:5]
        ref_alleles = snp_annotations[:, 3]
        n_snps = len(snp_ids)

#    print (snp_ids, chromosomes, positions, ref_alleles)
    if skip_gene is True:
        return
    
    # if step is not a multiple of n_snps, remove some snps from the beginning and the ned
    if central_window_only is True:
        if options.windows_size == 0:
            windows_size = n_snps   
            step = n_snps
            skipped_initial_snps = 0
        else:
            windows_size = options.windows_size
            step = windows_size
            skipped_initial_snps = (n_snps / 2) - (windows_size / 2)
        n_snps = skipped_initial_snps + windows_size
#        print (skipped_initial_snps, n_snps, step)
#        print range(skipped_initial_snps, n_snps, step)
    else:
        if options.windows_size == 0:
            windows_size = n_snps 
            step = n_snps
            skipped_initial_snps = 0
        else:
            windows_size = options.windows_size
            if options.overlapping is not True:
                # non-overlapping windows
                step = windows_size
            else:
                step = 1
            skipped_initial_snps = int((n_snps % step) / 2)

    if options.use_hdf5 is False:
        try:
            all_genotypes, individuals, individuals_dict, gene_name = parse_binary_file(allpops_binaryfile, individuals_dict)
        except:
            return None
    elif options.use_hdf5 is True:
        try:
            all_genotypes, individuals, individuals_dict, gene_name = parse_hdf5_file(allpops_binaryfile, individuals_dict)
        except:
            return None

#    print "genotypes parsed"
#    print all_genotypes[0:5]
    original_random_seed = random_seed
    for window_start in range(skipped_initial_snps, n_snps, step):
        window_end = window_start+windows_size
        random_seed = original_random_seed
#        print skipped_initial_snps, step, window_start, window_end
#        print ">", gene, window_start, window_end, windows_size, n_snps
#        print window_end < n_snps
        if window_end > n_snps:
            continue

        try:

            # GENERATE NETWORK AND CALCULATE PROPERTIES
            allpops_network = generate_network(
                                            all_genotypes = all_genotypes,
                                            individuals = individuals,
                                            individuals_dict = individuals_dict,
                                            gene_name = gene_name,
#                                            individuals_dict=individuals_dict, 
                                            distance = options.distance, 
                                            upstream = window_start+1, #NOTE: window_start is corrected in generate_network. For this reason, I am adding +1 here
                                            downstream = window_end,
                                            use_hdf5 = options.use_hdf5)
            allpops_network['filename'] = allpops_binaryfile.name
            allpops_network['file_prefix'] = gene_name
            allpops_network[phenotype] = 'glob'
        except GenotypeNetworkInitError:
            # skip the current window
            continue

        window_label = 'window_' + str(window_start / step) 
#        networks[gene]['glob'][window_label] = allpops_network
        allpops_network['window'] = window_label
        allpops_network['whole_gene_nsnps'] = n_snps
        allpops_network['gene'] = gene
        if snp_ids != []:
            allpops_network['snp_ids'] = snp_ids[window_start:window_end]
        else:
            allpops_network['snp_ids'] = ['NA'] * windows_size
        if chromosomes != []:
            allpops_network['chromosomes'] = chromosomes[window_start:window_end]
        else:
            allpops_network['chromosomes'] = ['NA'] * windows_size
        if positions != []:
            allpops_network['positions'] = positions[window_start:window_end]
            allpops_network['distance_from_upstream_margin'] = min(positions[window_start:window_end]) - min(positions)
            allpops_network['distance_from_downstream_margin'] = max(positions) - max(positions[window_start:window_end])
        else:
            allpops_network['positions'] = [numpy.nan] * windows_size
            allpops_network['distance_from_upstream_margin'] = numpy.nan
            allpops_network['distance_from_downstream_margin'] = numpy.nan
        if ref_alleles != []:
            allpops_network['ref_allele'] = ref_alleles[window_start:window_end]
        else:
            allpops_network['ref_allele'] = ['N'] * windows_size


        # PRINT REPORT TO STDOUT
        if report_type == 'values_by_window':
#            report_output += allpops_network.csv_report(report_fields)
#            print allpops_network
            print allpops_network.csv_report(report_fields)
        if report_type == 'values_by_node':
#            report_output += allpops_network.values_by_node(report_fields, header=False)
            print allpops_network.values_by_node(report_fields, header=False)
#        if report_type == "individuals":
#            pass
#            print "-----"
#            print gene_name, "allpops"
#            for ind in allpops_network['individuals']:
#                ind_key = ind.replace('_1', '').replace('_2', '')
#                print ind, individuals_dict[ind_key]['continent'],
#                print individuals_dict[ind_key]['subpop']

        if options.use_hdf5 is False:
            allpops_binaryfile.seek(0)




# SUBSAMPLING BY POPULATION OR PHENOTYPE
        if phenotype == 'continent':
            pops = allpops_network['allcontinents']
        else:
            if allpops_network['allphenotype_statuses'].has_key(phenotype):
                pops = allpops_network['allphenotype_statuses'][phenotype]
            else:
                raise InvalidPhenotype("""

    The phenotype selected is not defined in the input file you provided. Check the individuals file

    This is the phenotype you requested: {0}. There is no column for this phenotype in {1}.

""".format(phenotype, options.individuals_file), options.individuals_file, phenotype)

        if options.n_individuals > 0:
            pops.insert(0, 'global_sub')
#        print pops
        output = ""
#        report_fields.replace("continent", phenotype)
        for pop in pops:
#            print pop

            random_seed = sum([ord(l) for l in pop]) + random_seed # make sure that a different (yet reproducible) seed is used for every resampling
#            print random_seed
            subnetwork = allpops_network.subgraph_by_phenotype(phenotype, pop, n_individuals=options.n_individuals, random_seed=random_seed)
            if subnetwork is None:
                continue
            subnetwork[phenotype] = pop
#            print subnetwork.attributes
            if subnetwork is not None and subnetwork.vcount() > 0:
                if report_type == 'values_by_window':
                    print subnetwork.csv_report(report_fields)
                if report_type == 'values_by_node':
                    print subnetwork.values_by_node(report_fields, header=False)
                if report_type == "individuals_line":
                    output += "-----"
                    output += gene_name + ' ' + pop + ' '
                    for ind in subnetwork['individuals']:
                        ind_key = ind.replace('_1', '').replace('_2', '')
#                        output += ' ' + ind + ' ' + individuals_dict[ind_key]['continent'] + ' '
                        output += ' ' + ind + ' ' + individuals_dict[ind_key]['continent'] + ' '
                        output += individuals_dict[ind_key]['subpop'] + ' '

                if report_type == "individuals":
                    print "-----"
                    print gene_name, pop
                    for ind in subnetwork['individuals']:
                        ind_key = ind.replace('_1', '').replace('_2', '')
#                        print ind, individuals_dict[ind_key]['continent'], 
                        print ind, individuals_dict[ind_key]['continent'], 
                        print individuals_dict[ind_key]['subpop']

        if report_type == "individuals_line":
            print output




if __name__ == '__main__':
    (binary_file_path, options) = get_options()
    individuals_dict = parse_individuals_file(options.individuals_file)
    logging.debug("starting parsing {0}".format(binary_file_path))
    if options.use_hdf5 is False:
        all_genotypes, individuals, individuals_individuals_dict, gene_name = parse_binary_file(binary_file_path, individuals_dict)
    elif options.use_hdf5 is True:
        raise NotImplemented
        all_genotypes, individuals, individuals_individuals_dict, gene_name = parse_hdf5_file(open(binary_file_path, 'r'), individuals_dict)
    network = generate_network(all_genotypes, individuals,
            individuals_dict, gene_name=gene_name,
            distance=options.distance, upstream=options.upstream, 
            downstream=options.downstream)
    logging.debug("network parsed correctly. Starting writing csv report")
    print network.csv_report()


