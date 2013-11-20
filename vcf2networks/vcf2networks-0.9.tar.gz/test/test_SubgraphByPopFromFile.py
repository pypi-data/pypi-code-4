#!/usr/bin/env python
"""
"""
from test_SubgraphByPop import SimpleNetwork
import binary_to_network
import nose
import numpy

class SimpleNetworkFromFile(SimpleNetwork):
    binary_genotypes_file = 'test/test_data/binary_genotypes/MOGS.binary'
    individuals_file = 'test/test_data/phase1_integrated_calls.20101123.ALL.panel.individuals'

    expected_str_by_pop = {
                    'glob' : "Genotype Network (name = 'MOGS', chromosome lenght = 7, |V| = 13, |E| = 14)",
                    "AMR": "Genotype Network (name = 'MOGS_AMR', chromosome lenght = 7, |V| = 10, |E| = 8)",
                    "ASN": "Genotype Network (name = 'MOGS_ASN', chromosome lenght = 7, |V| = 7, |E| = 6)",
                    "EUR": "Genotype Network (name = 'MOGS_EUR', chromosome lenght = 7, |V| = 8, |E| = 5)",
                    "AFR": "Genotype Network (name = 'MOGS_AFR', chromosome lenght = 7, |V| = 8, |E| = 7)"
    }
    expected_report_by_pop = {
                    'glob': "MOGS glob 7 2184 13 14 1 5 0.1795 168.0 2.7692 2.1538 5 10.6154 0.3729",
                    "AMR": "MOGS_AMR AMR 7 362 10 8 3 3 0.1778 36.2 1.5625 1.6 3 0.9 0.1456",
                    "ASN": "MOGS_ASN ASN 7 572 7 6 2 2 0.2857 81.7143 1.3333 1.7143 2 0.4286 0.221",
                    "EUR": "MOGS_EUR EUR 7 758 8 5 3 2 0.1786 94.75 1.4444 1.25 3 0.5 0.1731",
                    "AFR": "MOGS_AFR AFR 7 370 8 7 1 4 0.25 46.25 2.25 1.75 4 4.375 0.465"
    }
    expected_nodes_by_pop = {
                    'glob': ['0000000', '0000001', '0000100', '0011000', '0000010', '0011001', '0011100', '0111000', '0011010', '1010000', '0000110', '0000101', '0010000'],
                    'AMR': ['0000000', '0000001', '0000100', '0011000', '0000010', '0011001', '0011100', '0111000', '1010000', '0000110'],
                    'ASN': ['0000000', '0000001', '0000100', '0011000', '0011001', '0011100', '0000101'],
                    'EUR': ['0000000', '0000001', '0000100', '0011000', '0000010', '0011001', '0011100', '1010000'],
                    'AFR': ['0000000', '0000100', '0011000', '0011100', '0111000', '0011010', '1010000', '0010000']
    }


    expected_n_datapoints_by_pop = {
                    'glob': [956, 55, 26, 934, 44, 7, 42, 63, 18, 34, 2, 1, 2],
                    'AMR': [1, 2, 3, 4, 6, 9, 10, 41, 83, 203],
                    'ASN': [1, 2, 2, 2, 18, 98, 449],
                    'EUR': [1, 3, 4, 5, 13, 41, 105, 586],
                    'AFR': [1, 2, 12, 16, 27, 38, 53, 221]
#                    'AFR': [69, 2, 2, 297, 13, 59, 18, 30, 2]
    }

    expected_diameter_by_pop = {
                    "glob" : 5,
                    "AMR": 3,
                    "ASN": 2,
                    "EUR": 2,
                    "AFR": 4,
    }
    expected_avdegree_by_pop = {
                    'glob': 2.1538,
                    'AMR': 1.6,
                    'ASN': 1.7143,
                    'EUR': 1.25,
                    'AFR': 1.75
    }
    expected_av_w_degree_by_pop = {
                    'glob': 0.3151,
                    'AMR': 0.2715,
                    'ASN': 0.2807,
                    'EUR': 0.3354,
                    'AFR': 0.3625
    }


    individuals_dict = binary_to_network.parse_individuals_file(individuals_file, pickle_from_file_if_possible=False) #TODO: de-activate pickling of this variable
    all_genotypes, individuals, individuals_dict, gene_name = binary_to_network.parse_binary_file(
        binary_genotypes_file, individuals_dict)
    network = binary_to_network.generate_network(all_genotypes, individuals, individuals_dict, gene_name) 
#    network = binary_to_network.generate_network(binary_genotypes_file, individuals_dict) 

    def setUp(self):
#        delattr(self, test_NodesIndividuals)
#        print self.network.vs['genotype']
        self.subgraphs = {}
        self.network.__calculate_network_properties__()
        self.pops = ("AMR", "ASN", "EUR", "AFR")
        for pop in self.pops:
            self.subgraphs[pop] = self.network.subgraph_by_continent(pop)
            self.subgraphs[pop].__calculate_network_properties__()
            print pop, self.subgraphs[pop].vs()['genotype']

    def test_NodesIndividuals(self):
        self.skipTest("Individuals test skipped, because there are too many individuals")

class DPAGT1SimpleNetworkFromHDF5File(SimpleNetwork):
    hdf5_genotypes_file = 'test/test_data/hdf5/DPAGT1_genotypes.hdf5'
    individuals_file = 'test/test_data/phase1_integrated_calls.20101123.ALL.panel.individuals'

    expected_str_by_pop = {
                    'glob' : "Genotype Network (name = 'DPAGT1', chromosome lenght = 11, |V| = 20, |E| = 15)",
                    "AMR": "Genotype Network (name = 'DPAGT1_AMR', chromosome lenght = 11, |V| = 7, |E| = 3)",
                    "ASN": "Genotype Network (name = 'DPAGT1_ASN', chromosome lenght = 11, |V| = 9, |E| = 2)",
                    "EUR": "Genotype Network (name = 'DPAGT1_EUR', chromosome lenght = 11, |V| = 7, |E| = 3)",
                    "AFR": "Genotype Network (name = 'DPAGT1_AFR', chromosome lenght = 11, |V| = 14, |E| = 11)"
    }
    expected_report_by_pop = {
                    'glob': "DPAGT1 glob 11 2184 20 15 6 7 0.0789 109.2 3.25 1.5 5 10.35 0.0973",
                    'AMR': "DPAGT1_AMR AMR 11 362 7 3 4 2 0.1429 51.7143 1.25 0.8571 2 0.1429 0.1723",
                    "ASN": "DPAGT1_ASN ASN 11 572 9 2 7 1 0.0556 63.5556 1.0 0.4444 1 0.0 0.1173",
                    "EUR": "DPAGT1_EUR EUR 11 758 7 3 4 2 0.1429 108.2857 1.25 0.8571 2 0.1429 0.1723",
                    "AFR": "DPAGT1_AFR AFR 11 370 14 11 4 6 0.1209 26.4286 2.8364 1.5714 5 7.2143 0.1615"
    }
    expected_nodes_by_pop = {
                    'glob': ['00000000000', '00000000100', '00000000101', 
                        '00000000111', '00000001111', '00000110101', 
                        '00001000100', '00010000100', '00010000101', 
                        '00110000101', '00110100101', '00110110101', 
                        '00111001111', '01110000101', '01110001000', 
                        '01110001110', '01110001111', '01110110101', 
                        '10000000100', '10000100101'],
                    'AMR': ['00000000100', '00110110101', '01110001111', 
                        '00000000000', '00110000101', '00110100101', 
                        '00000000111'],
                    'ASN': ['00000000100', '00110110101', '01110001111', 
                        '00000000000', '00110000101', '00000110101', 
                        '01110001000', '01110110101', '00000001111'], 
                    'EUR': ['00000000100', '00110110101', '01110001111', 
                        '00000000000', '10000100101', '00000000101', 
                        '01110001110'], 
                    'AFR': ['00000000100', '00110110101', '01110001111', 
                        '00000000000', '10000100101', '00110000101', 
                        '00111001111', '00010000100', '00110100101', 
                        '00000000101', '10000000100', '01110000101', 
                        '00001000100', '00010000101']
    }


    expected_n_datapoints_by_pop = {
                    'glob': [952, 164, 721, 248, 25, 11, 1, 20, 1, 3, 7, 8, 14, 1, 2, 1, 1, 2, 1, 1],
                    'AMR': [1, 1, 2, 19, 24, 100, 215],
                    'ASN': [67, 64, 279, 146, 6, 1, 1, 7, 1],
                    'EUR': [367, 45, 288, 50, 6, 1, 1],
                    'AFR': [225, 22, 38, 27, 15, 3, 17, 3, 7, 8, 1, 1, 2, 1]
    }

    expected_diameter_by_pop = {
                    "glob" : 7,
                    "AMR": 2,
                    "ASN": 1,
                    "EUR": 2,
                    "AFR": 6,
    }
    expected_avdegree_by_pop = {
                    'glob': 1.5,
                    'AMR': 0.8571,
                    'ASN': 0.4444,
                    'EUR': 0.8571,
                    'AFR': 1.5714
    }
    expected_av_w_degree_by_pop = {
                    'glob': 0.1413,
                    'AMR': 0.1034,
                    'ASN': 0.0552,
                    'EUR': 0.2024,
                    'AFR': 0.2367
    }

    individuals_dict = binary_to_network.parse_individuals_file(
        individuals_file, pickle_from_file_if_possible=False)
    hdf5_genotypes_file = open(hdf5_genotypes_file, 'r')
    all_genotypes, individuals, individuals_dict, gene_name = binary_to_network.parse_hdf5_file(
        hdf5_genotypes_file, individuals_dict)
    network = binary_to_network.generate_network(all_genotypes, individuals, individuals_dict, gene_name, use_hdf5=True) 
#    network = binary_to_network.generate_network(binary_genotypes_file, individuals_dict) 

    def setUp(self):
#        delattr(self, test_NodesIndividuals)
#        print self.network.vs['genotype']
        self.subgraphs = {}
        self.network.__calculate_network_properties__()
        self.pops = ("AMR", "ASN", "EUR", "AFR")
        for pop in self.pops:
            self.subgraphs[pop] = self.network.subgraph_by_continent(pop)
            self.subgraphs[pop].__calculate_network_properties__()
            print pop, self.subgraphs[pop].vs()['genotype']

    def test_NodesIndividuals(self):
        self.skipTest("Individuals test skipped, because there are too many individuals")


class SimpleNetworkFromHDF5File(SimpleNetwork):
    hdf5_genotypes_file = 'test/test_data/hdf5/MOGS_genotypes.hdf5'
    individuals_file = 'test/test_data/phase1_integrated_calls.20101123.ALL.panel.individuals'

    expected_str_by_pop = {
                    'glob' : "Genotype Network (name = 'MOGS', chromosome lenght = 7, |V| = 13, |E| = 14)",
                    "AMR": "Genotype Network (name = 'MOGS_AMR', chromosome lenght = 7, |V| = 10, |E| = 8)",
                    "ASN": "Genotype Network (name = 'MOGS_ASN', chromosome lenght = 7, |V| = 7, |E| = 6)",
                    "EUR": "Genotype Network (name = 'MOGS_EUR', chromosome lenght = 7, |V| = 8, |E| = 5)",
                    "AFR": "Genotype Network (name = 'MOGS_AFR', chromosome lenght = 7, |V| = 8, |E| = 7)"
    }
    expected_report_by_pop = {
                    'glob': "MOGS glob 7 2184 13 14 1 5 0.1795 168.0 2.7692 2.1538 5 10.6154 0.3729",
                    "AMR": "MOGS_AMR AMR 7 362 10 8 3 3 0.1778 36.2 1.5625 1.6 3 0.9 0.1456",
                    "ASN": "MOGS_ASN ASN 7 572 7 6 2 2 0.2857 81.7143 1.3333 1.7143 2 0.4286 0.221",
                    "EUR": "MOGS_EUR EUR 7 758 8 5 3 2 0.1786 94.75 1.4444 1.25 3 0.5 0.1731",
                    "AFR": "MOGS_AFR AFR 7 370 8 7 1 4 0.25 46.25 2.25 1.75 4 4.375 0.465"
    }
    expected_nodes_by_pop = {
                    'glob': ['0000000', '0000001', '0000100', '0011000', '0000010', '0011001', '0011100', '0111000', '0011010', '1010000', '0000110', '0000101', '0010000'],
                    'AMR': ['0000000', '0000001', '0000100', '0011000', '0000010', '0011001', '0011100', '0111000', '1010000', '0000110'],
                    'ASN': ['0000000', '0000001', '0000100', '0011000', '0011001', '0011100', '0000101'],
                    'EUR': ['0000000', '0000001', '0000100', '0011000', '0000010', '0011001', '0011100', '1010000'],
                    'AFR': ['0000000', '0000100', '0011000', '0011100', '0111000', '0011010', '1010000', '0010000']
    }


    expected_n_datapoints_by_pop = {
                    'glob': [956, 55, 26, 934, 44, 7, 42, 63, 18, 34, 2, 1, 2],
                    'AMR': [1, 2, 3, 4, 6, 9, 10, 41, 83, 203],
                    'ASN': [1, 2, 2, 2, 18, 98, 449],
                    'EUR': [1, 3, 4, 5, 13, 41, 105, 586],
                    'AFR': [1, 2, 12, 16, 27, 38, 53, 221]
#                    'AFR': [69, 2, 2, 297, 13, 59, 18, 30, 2]
    }

    expected_diameter_by_pop = {
                    "glob" : 5,
                    "AMR": 3,
                    "ASN": 2,
                    "EUR": 2,
                    "AFR": 4,
    }
    expected_avdegree_by_pop = {
                    'glob': 2.1538,
                    'AMR': 1.6,
                    'ASN': 1.7143,
                    'EUR': 1.25,
                    'AFR': 1.75
    }
    expected_av_w_degree_by_pop = {
                    'glob': 0.3151,
                    'AMR': 0.2715,
                    'ASN': 0.2807,
                    'EUR': 0.3354,
                    'AFR': 0.3625
    }

    individuals_dict = binary_to_network.parse_individuals_file(
        individuals_file, pickle_from_file_if_possible=False)
    hdf5_genotypes_file = open(hdf5_genotypes_file, 'r')
    all_genotypes, individuals, individuals_dict, gene_name = binary_to_network.parse_hdf5_file(
        hdf5_genotypes_file, individuals_dict)
    network = binary_to_network.generate_network(all_genotypes, individuals, individuals_dict, gene_name, use_hdf5=True) 
#    network = binary_to_network.generate_network(binary_genotypes_file, individuals_dict) 

    def setUp(self):
#        delattr(self, test_NodesIndividuals)
#        print self.network.vs['genotype']
        self.subgraphs = {}
        self.network.__calculate_network_properties__()
        self.pops = ("AMR", "ASN", "EUR", "AFR")
        for pop in self.pops:
            self.subgraphs[pop] = self.network.subgraph_by_continent(pop)
            self.subgraphs[pop].__calculate_network_properties__()
            print pop, self.subgraphs[pop].vs()['genotype']

    def test_NodesIndividuals(self):
        self.skipTest("Individuals test skipped, because there are too many individuals")


#from nose.plugins.attrib import attr
#@attr('slow')
@nose.plugins.attrib.attr('slow')
def test_SubgraphingWorks():
    """check that the function subgraph_by_continent works, without checking all the details as in the other TestCase of this file.
    
    NOTE: RPN2 is very slow"""
    individuals_file = 'test/test_data/phase1_integrated_calls.20101123.ALL.panel.individuals'
    individuals_dict = binary_to_network.parse_individuals_file(individuals_file, pickle_from_file_if_possible=False) #TODO: de-activate pickling of this variable

    genes = 'FUT8 TUSC3 RPN2'.split()
    pops = ("AMR", "ASN", "EUR", "AFR")
    for gene in genes: 
        for pop in pops:
            binary_genotypes_file = 'test/test_data/binary_genotypes/{0}.binary'.format(gene)
            all_genotypes, individuals, individuals_dict, gene_name = binary_to_network.parse_binary_file(
                binary_genotypes_file, individuals_dict)
            network = binary_to_network.generate_network(all_genotypes, individuals, individuals_dict, gene_name) 
#            network = binary_to_network.generate_network(binary_genotypes_file, individuals_dict) 
            yield check_Subgraphing, pop, network, individuals_dict

def check_Subgraphing(pop, network, individuals_dict):
    subnetwork = network.subgraph_by_continent(pop)
    assert (subnetwork.vcount() > 0)





if __name__ == '__main__':
    import logging
    import doctest
    logging.basicConfig(level=logging.DEBUG)
    doctest.testmod()


