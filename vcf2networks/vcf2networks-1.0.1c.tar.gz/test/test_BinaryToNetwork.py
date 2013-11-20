#!/usr/bin/env python
"""
"""
#from test_SubgraphByPop import SimpleNetwork
import binary_to_network
import unittest
import nose
import subprocess
import logging
from src.GenotypeNetwork import GenotypeNetworkInitError
logging.basicConfig(level=logging.DEBUG)

class SimpleNetworkFromFile(unittest.TestCase):
    gene_name = 'ALG3'
    binary_genotypes_file = 'test/test_data/binary_genotypes/{0}.binary'.format(gene_name)
    individuals_file = 'test/test_data/phase1_integrated_calls.20101123.ALL.panel.individuals'

    expected_genotypes = ['0000000000000000', '1010000100000010', '0000000100000000', '1010000100000000', '0010101100001001', '0010000100000010', '0001000000000000', '0000000000000100', '1010010111010000', '0010000100100010', '1010010110010000', '1110010111010000', '0000000000000010', '0010000000000000', '0010000100000000', '0110010111010000', '0010010110010000', '0010010100100010', '1010000000000000', '1010010100100010', '1010000100000100', '1010000110010000']


    individuals_dict = binary_to_network.parse_individuals_file(individuals_file, pickle_from_file_if_possible=False) #TODO: de-activate pickling of this variable

    def setUp(self):
#        self.network = binary_to_network.generate_network(self.binary_genotypes_file, self.individuals_dict) 
        self.all_genotypes, self.individuals, self.individuals_dict, self.gene_name = binary_to_network.parse_binary_file(
                    self.binary_genotypes_file, self.individuals_dict)
        print self.binary_genotypes_file
        self.network = binary_to_network.generate_network(self.all_genotypes, self.individuals, self.individuals_dict, self.gene_name) 

    def test_Genotypes(self):
        print self.expected_genotypes
        print self.network.vs['genotype']
#        nose.tools.assert_sequence_equal(self.expected_genotypes, self.network.vs['genotype'])
        nose.tools.assert_equal(self.expected_genotypes, self.network.vs['genotype'])

    def test_Windows515(self):
        """test a window from position 5 to 15"""
        upstream = 5
        downstream = 15
#        self.network_window1 = binary_to_network.generate_network(self.binary_genotypes_file, self.individuals_dict, upstream=upstream, downstream=downstream) 
        logging.debug (("expected length:10 or less AAAAAAAAAAAAAAAA", self.all_genotypes[0:10]))
        self.network_window1 = binary_to_network.generate_network(self.all_genotypes, self.individuals, self.individuals_dict, self.gene_name, upstream=upstream, downstream=downstream) 
        expected_genotypes_window1 = set([g[upstream-1:downstream] for g in self.expected_genotypes])
        network_window1_genotypes = set(self.network_window1.vs['genotype'])
        nose.tools.assert_equal(expected_genotypes_window1.difference(network_window1_genotypes), set([]))

    def test_WindowsEndIsBiggerThanChromosomeLength(self):
        upstream = 5
        downstream = 1000
        self.network_window1 = binary_to_network.generate_network(self.all_genotypes, self.individuals, self.individuals_dict, self.gene_name, upstream=upstream, downstream=downstream) 
        expected_genotypes_window1 = set([g[upstream-1:len(self.expected_genotypes[0])] for g in self.expected_genotypes])
        network_window1_genotypes = set(self.network_window1.vs['genotype'])
        nose.tools.assert_equal(expected_genotypes_window1.difference(network_window1_genotypes), set([]))

    @nose.tools.raises(ValueError)
    def test_WindowsStartisBiggerThanEnd(self):
        upstream = 20
        downstream = 5
        self.network_window1 = binary_to_network.generate_network(self.all_genotypes, self.individuals, self.individuals_dict, self.gene_name, upstream=upstream, downstream=downstream) 

    def test_WindowsEndIsNone(self):
        upstream = 5
        downstream = None
        self.network_window1 = binary_to_network.generate_network(self.all_genotypes, self.individuals, self.individuals_dict, self.gene_name, upstream=upstream, downstream=downstream) 
        expected_genotypes_window1 = set([g[upstream-1:len(self.expected_genotypes[0])] for g in self.expected_genotypes])
        network_window1_genotypes = set(self.network_window1.vs['genotype'])
        nose.tools.assert_equal(expected_genotypes_window1.difference(network_window1_genotypes), set([]))

    def test_WindowsStartIsNone(self):
        upstream = None
        downstream = 15
        self.network_window1 = binary_to_network.generate_network(self.all_genotypes, self.individuals, self.individuals_dict, self.gene_name, upstream=upstream, downstream=downstream) 
        expected_genotypes_window1 = set([g[0:downstream] for g in self.expected_genotypes])
        network_window1_genotypes = set(self.network_window1.vs['genotype'])
        print expected_genotypes_window1
        print network_window1_genotypes
        nose.tools.assert_equal(expected_genotypes_window1.difference(network_window1_genotypes), set([]))

    def test_WindowsStartAndEndAreNone(self):
        upstream = None
        downstream = None
        self.network_window1 = binary_to_network.generate_network(self.all_genotypes, self.individuals, self.individuals_dict, self.gene_name, upstream=upstream, downstream=downstream) 
        expected_genotypes_window1 = set([g for g in self.expected_genotypes])
        network_window1_genotypes = set(self.network_window1.vs['genotype'])
        nose.tools.assert_equal(expected_genotypes_window1.difference(network_window1_genotypes), set([]))


class MOGS(SimpleNetworkFromFile):
    gene_name = 'MOGS'
    binary_genotypes_file = 'test/test_data/binary_genotypes/{0}.binary'.format(gene_name)
    individuals_file = 'test/test_data/phase1_integrated_calls.20101123.ALL.panel.individuals'
    expected_genotypes = ['0000000', '0000001', '0000100', '0011000', '0000010', '0011001', '0011100', '0111000', '0011010', '1010000', '0000110', '0000101', '0010000']
    individuals_dict = binary_to_network.parse_individuals_file(individuals_file, pickle_from_file_if_possible=False) #TODO: de-activate pickling of this variable


#@nose.tools.raises(src.GenotypeNetwork.GenotypeNetworkInitError)
#@nose.tools.raises(GenotypeNetworkInitError)
def test_ALG13_triallelicSNPs():
    """
    Test that creating a network from ALG13, which has only invalid genotypes, returns an Error

    ALG13 contains some "2" in the genotypes. 
    Unfortunately this file doesn't have any valid genotype.
    """
    gene_name = 'ALG13'
    binary_genotypes_file = 'test/test_data/binary_genotypes/{0}.binary'.format(gene_name)
    individuals_file = 'test/test_data/phase1_integrated_calls.20101123.ALL.panel.individuals'
    individuals_dict = binary_to_network.parse_individuals_file(individuals_file, pickle_from_file_if_possible=False) #TODO: de-activate pickling of this variable
    all_genotypes, individuals, individuals_dict, gene_name = binary_to_network.parse_binary_file(binary_genotypes_file, individuals_dict)
#    with nose.tools.raises(GenotypeNetworkInitError):
    with nose.tools.raises(src.GenotypeNetwork.GenotypeNetworkInitError):
        network = binary_to_network.generate_network(all_genotypes, individuals, individuals_dict, gene_name) 
#    network = binary_to_network.generate_network(binary_genotypes_file, individuals_dict) 


#def test_StartAndEndPositions():
#    """
#    generate networks by varying the upstream and downstream positions
#    """


#def check_BinaryToNetworkCommandLineInterface():
#    comms = ['python src/binary_to_network -f ']

       
if __name__ == '__main__':
    import logging
    import doctest
    logging.basicConfig(level=logging.DEBUG)
    doctest.testmod()


