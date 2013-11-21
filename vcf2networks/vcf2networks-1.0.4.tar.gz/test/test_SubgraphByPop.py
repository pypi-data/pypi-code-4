#!/usr/bin/env python
"""
"""
import unittest
import nose
from GenotypeNetwork import *

import numpy
#testcases = {
class SimpleNetwork(unittest.TestCase):
    """
    Basic test case representing a simple network, composed of 5 genotypes on 3 SNPs.

    All the other test cases are derived from this case. 
    The attributes name, chromosome_len, genotypes, individuals, individuals_dict are used to build the network. 
    All the other attributes that have a name beginning with "expected_" are used for testing. They represent the expected values that the network and its subgraphs should have, and they should be calculated by hand. If some of these attributes don't match, the testing suite will return an error.

    """
    # Network definition
    name = "simple_network"
    chromosome_len = 3
#                   EUR    EUR    AFR    AFR    AFR
    genotypes =   ['001', '000', '000', '000', '010']
    individuals = ['HG1', 'HG2', 'HG3', 'HG4', 'HG5']
    individuals_dict = {
                    'HG1': {'continent': 'EUR', 'subpop': 'TSC', 'phenotype1': 'good'}, 
                    'HG2': {'continent': 'EUR', 'subpop': 'GBR', 'phenotype1': 'bad'}, 
                    'HG3': {'continent': 'AFR', 'subpop': 'AFR', 'phenotype1': 'good'}, 
                    'HG4': {'continent': 'AFR', 'subpop': 'YRI', 'phenotype1': 'good'}, 
                    'HG5': {'continent': 'AFR', 'subpop': 'YRI', 'phenotype1': 'good'}, 
    }

    # Expected values
    expected_str_by_pop = {
                    'glob' : "Genotype Network (name = 'simple_network', chromosome lenght = 3, |V| = 3, |E| = 2)",
                    "AMR": "Genotype Network (name = 'simple_network_AMR', chromosome lenght = 3, |V| = 0, |E| = 0)",
                    "ASN": "Genotype Network (name = 'simple_network_ASN', chromosome lenght = 3, |V| = 0, |E| = 0)",
                    "EUR": "Genotype Network (name = 'simple_network_EUR', chromosome lenght = 3, |V| = 2, |E| = 1)",
                    "AFR": "Genotype Network (name = 'simple_network_AFR', chromosome lenght = 3, |V| = 2, |E| = 1)",
    }
    expected_report_by_pop = {
                    'glob': "simple_network glob 3 5 3 2 1 2 0.6667 1.6667 1.3333 1.3333 2 0.3333 0.7778",
                    'AMR': "simple_network_AMR AMR 3 0 0 0 0 0 nan nan nan nan 0 nan nan",
                    'ASN': "simple_network_ASN ASN 3 0 0 0 0 0 nan nan nan nan 0 nan nan",
                    'EUR': "simple_network_EUR EUR 3 2 2 1 1 1 1.0 1.0 1.0 1.0 1 0.0 1.0",
                    'AFR': "simple_network_AFR AFR 3 3 2 1 1 1 1.0 1.5 1.0 1.0 1 0.0 1.0"
    }
    expected_nodes_by_pop = {
                    'glob': ['001', '000', '010'],
                    'AMR': [],
                    'ASN': [],
                    'EUR': ['001', '000'],
                    'AFR': ['000', '010']
    }

    expected_individuals_by_pop = {
                    'glob': [['HG1'], ['HG2', 'HG3', 'HG4'], ['HG5']],
                    'AMR': [],
                    'ASN': [],
                    'EUR': [['HG1'], ['HG2']],
                    'AFR': [['HG3', 'HG4'], ['HG5']]
    }

    expected_n_datapoints_by_pop = {
                    'glob': [1,3,1],
                    'AMR': [],
                    'ASN': [],
                    'EUR': [1, 1],
                    'AFR': [2, 1]
    }
    expected_diameter_by_pop = {
                    'glob': 2,
                    'AMR': 0,
                    'ASN': 0,
                    'EUR': 1,
                    'AFR': 1
    }
    expected_avdegree_by_pop = {
                    'glob': round((1 + 2 + 1) / 3., 4),
                    'AMR': numpy.nan,
                    'ASN': numpy.nan,
                    'EUR': (1*1 + 1*1) / 2.,
                    'AFR': (1*1 + 1*1) / 2.
    }
    expected_av_w_degree_by_pop = {
                    'glob': round(((1./5)*1 + (2./5)*3 + (1./5)*1) / 3., 4),
                    'AMR': numpy.nan,
                    'ASN': numpy.nan,
#                    'EUR': (1./5) + (1./5),
                    'EUR': 1/2.,
                    'AFR': ((2./3)*1 + (1./3)*1) / 2.
    }

    def setUp(self): # TODO: see if you can use setUpAll
        self.network = GenotypeNetwork(self.chromosome_len, name = self.name)
        self.network.populate_from_binary_strings_and_individuals(genotypes=self.genotypes, individuals=self.individuals, 
                                individuals_dict=self.individuals_dict)
        self.network.__calculate_network_properties__()
        self.subgraphs = {}
        self.pops = ("AMR", "ASN", "EUR", "AFR")
        for pop in self.pops:
            self.subgraphs[pop] = self.network.subgraph_by_continent(pop)
            self.subgraphs[pop].__calculate_network_properties__()

    def test_NodesNames(self):
        self.assertEquals(sorted(self.network.vs['genotype']), sorted(self.expected_nodes_by_pop['glob']))
        for pop in self.pops:
            print self.subgraphs[pop]
            self.assertEquals(sorted(self.subgraphs[pop].vs['genotype']), sorted(self.expected_nodes_by_pop[pop]))

    def test_NodesDensities(self):
        self.assertEquals(self.network.vs['n_datapoints'], self.expected_n_datapoints_by_pop['glob'])
        for pop in self.pops:
            print pop, self.subgraphs[pop].vs['n_datapoints']
            self.assertEquals(sorted(self.subgraphs[pop].vs['n_datapoints']), sorted(self.expected_n_datapoints_by_pop[pop]))

    def test_NodesIndividuals(self):
        print self.network['name']
        for node in self.network.vs:
            print node['genotype']
            self.assertEquals(sorted(node['node_individuals']), sorted(self.expected_individuals_by_pop['glob'][node.index]))
        for pop in self.pops:
            print pop, self.subgraphs[pop].vs['node_individuals']
            for node in self.subgraphs[pop].vs:
                print node.index
                print node['node_individuals']
                self.assertEquals(sorted(node['node_individuals']), sorted(self.expected_individuals_by_pop[pop][node.index]))

    def test_DiameterByPop(self):
        """check that the diameter of each subgraph is calculated correctly.
        """
        print self.network.diameter()
        print self.network['name']
        self.assertEquals(self.network.diameter(), self.expected_diameter_by_pop['glob'])
        for pop in self.pops:
            print pop, self.subgraphs[pop].diameter(), self.expected_diameter_by_pop[pop] 
            nose.tools.assert_almost_equals(self.subgraphs[pop].diameter(), self.expected_diameter_by_pop[pop], places=10) 

    def test_AvDegreeByPop(self):
        """The Average Degree is the average of the degree of all the nodes, divided by the number of nodes
        """
        print self.network['name']
        print "global av_degree:", self.network['av_degree']
        print self.network['name']
        self.assertEquals(self.network['av_degree'], self.expected_avdegree_by_pop['glob'])
        for pop in self.pops:
            expected = self.expected_avdegree_by_pop[pop]
            observed = self.subgraphs[pop]['av_degree']
            print self.network['name'], pop, expected, observed
            if expected is numpy.nan:
                self.assertEquals(numpy.nan_to_num(expected), numpy.nan_to_num(observed))
            else:
                nose.tools.assert_almost_equals(expected, observed)


    def test_AvWeightedDegreeByPop(self):
        """The Average Degree is the average of the degree of all the nodes, divided by the number of nodes, multiplied by their frequency
        """
        print "global av_w_degree:", self.network['av_w_degree']
        print self.network['name']
        self.assertEquals(self.network['av_w_degree'], self.expected_av_w_degree_by_pop['glob'])
        for pop in self.pops:
            expected = self.expected_av_w_degree_by_pop[pop]
            observed = self.subgraphs[pop]['av_w_degree']
            print self.network['name'], pop, expected, observed
            if expected is numpy.nan:
                self.assertEquals(numpy.nan_to_num(expected), numpy.nan_to_num(observed))
            else:
                nose.tools.assert_almost_equals(expected, observed)


    def test_CSVReportByPop(self):
        print self.network.csv_report()
        for pop in self.pops:
            print self.subgraphs[pop].csv_report()
#            nose.tools.assert_sequence_equal( self.subgraphs[pop].csv_report(), self.expected_report_by_pop[pop])
            nose.tools.assert_equals( self.subgraphs[pop].csv_report(), self.expected_report_by_pop[pop])

    def test_CSVReportGlob(self):
        print self.network.csv_report()
#        nose.tools.assert_sequence_equal( self.network.csv_report(), self.expected_report_by_pop['glob'])
        nose.tools.assert_equals( self.network.csv_report(), self.expected_report_by_pop['glob'])

    def test_StrGlob(self):
        s = self.network.__str__()
        print s
#        nose.tools.assert_sequence_equal(s, self.expected_str_by_pop['glob'])
        nose.tools.assert_equals(s, self.expected_str_by_pop['glob'])

    def test_StrByPop(self):
        for pop in self.pops:
            observed = self.subgraphs[pop].__str__()
            expected = self.expected_str_by_pop[pop]
            print pop, observed, expected
#            nose.tools.assert_sequence_equal(observed, expected)
            nose.tools.assert_equals(observed, expected)
#        assert (1==2)

    def test_NObservations(self):
        """the sum of subpop node n_datapoints should be equal to the n_datapoints of the parent graph"""
#        parent_n_datapoints = sum(self.network.vs['n_datapoints'])
#        print parent_n_datapoints
        print [ind for ind in self.network['individuals'] if self.network['individuals_dict'][ind.replace('_1', '').replace('_2', '')]['continent'] in self.pops]
        parent_n_datapoints = len([ind for ind in self.network['individuals'] if self.network['individuals_dict'][ind.replace('_1', '').replace('_2', '')]['continent'] in self.pops])
#        pops_n_datapoints = sum([sum(pop_network['n_datapoints']) for pop_network in self.subgraphs[pop] for pop in self.pops]) 
        pops_n_datapoints = sum([sum(self.subgraphs[pop].vs['n_datapoints']) for pop in self.pops])
#        print pops_n_datapoints
#        for pop in self.pops:
#            print pop,
#            for genotype in self.subgraphs[pop].vs:
#                print len(genotype['node_individuals']), genotype['n_datapoints'],
#            print self.subgraphs[pop].vs['n_datapoints']
#        print [len(self.subgraphs[pop].vs['node_individuals']) for pop in self.pops]
        self.assertEquals(parent_n_datapoints, pops_n_datapoints)

class DiploidNetwork(SimpleNetwork):
#    self.network = GenotypeNetwork(3, 'sample_phenotype')
    name = "diploid_network"
    chromosome_len = 3
#                   EUR       EUR      EUR      EUR      AFR      AFR      AFR      AFR      AFR      AFR
    genotypes =   ['001',    '000',   '000',   '000',   '010',   '100',   '101',   '111',   '000',   '101']
    individuals = ['HG1_1', 'HG1_2', 'HG2_1', 'HG2_2', 'HG3_1', 'HG3_2', 'HG4_1', 'HG4_2', 'HG5_1', 'HG5_2']
    individuals_dict = {
                    'HG1': {'continent': 'EUR', 'subpop': 'TSC', 'phenotype1': 'good'}, 
                    'HG2': {'continent': 'EUR', 'subpop': 'GBR', 'phenotype1': 'bad'}, 
                    'HG3': {'continent': 'AFR', 'subpop': 'AFR', 'phenotype1': 'good'}, 
                    'HG4': {'continent': 'AFR', 'subpop': 'YRI', 'phenotype1': 'good'}, 
                    'HG5': {'continent': 'AFR', 'subpop': 'YRI', 'phenotype1': 'good'}, 
    }

    expected_str_by_pop = {
                    'glob' : "Genotype Network (name = 'diploid_network', chromosome lenght = 3, |V| = 6, |E| = 6)",
                    "AMR": "Genotype Network (name = 'diploid_network_AMR', chromosome lenght = 3, |V| = 0, |E| = 0)",
                    "ASN": "Genotype Network (name = 'diploid_network_ASN', chromosome lenght = 3, |V| = 0, |E| = 0)",
                    "EUR": "Genotype Network (name = 'diploid_network_EUR', chromosome lenght = 3, |V| = 2, |E| = 1)",
                    "AFR": "Genotype Network (name = 'diploid_network_AFR', chromosome lenght = 3, |V| = 5, |E| = 4)",
    }
    expected_report_by_pop = {
                    'glob': "diploid_network glob 3 10 6 6 1 4 0.4 1.6667 1.8667 2.0 3 2.1667 0.5556",
                    'AMR': "diploid_network_AMR AMR 3 0 0 0 0 0 nan nan nan nan 0 nan nan",
                    'ASN': "diploid_network_ASN ASN 3 0 0 0 0 0 nan nan nan nan 0 nan nan",
                    'EUR': "diploid_network_EUR EUR 3 4 2 1 1 1 1.0 2.0 1.0 1.0 1 0.0 1.0",
                    'AFR': "diploid_network_AFR AFR 3 6 5 4 1 4 0.4 1.2 2.0 1.6 2 2.0 0.5219"
    }
    expected_nodes_by_pop = {
                    'glob': ['001', '000', '010', '100', '101', '111'],
                    'AMR': [],
                    'ASN': [],
                    'EUR': ['000', '001'],
                    'AFR': ['000', '010', '100', '101', '111']
    }

    expected_individuals_by_pop = {
                    'glob': [['HG1_1'], ['HG1_2', 'HG2_1', 'HG2_2', 'HG5_1'], ['HG3_1'], ['HG3_2'], ['HG4_1', 'HG5_2'], ['HG4_2']], 
                    'AMR': [],
                    'ASN': [],
                    'EUR': [['HG1_1'], ['HG2_2', 'HG2_1', 'HG1_2']],
                    'AFR': [['HG5_1'], ['HG3_1'], ['HG3_2'], ['HG4_1', 'HG5_2'], ['HG4_2']]
    }

    expected_n_datapoints_by_pop = {
                    'glob': [1, 4, 1, 1, 2, 1],
                    'AMR': [],
                    'ASN': [],
                    'EUR': [1, 3],
                    'AFR': [1, 1, 1, 2, 1]
    }

    expected_diameter_by_pop = {
                    'glob': 4,
                    'AMR': 0,
                    'ASN': 0,
                    'EUR': 1,
                    'AFR': 4
    }
    expected_avdegree_by_pop = {
                    'glob': round((2 + 3 + 1 + 2 + 3 + 1)/6., 4),
                    'AMR': numpy.nan,
                    'ASN': numpy.nan,
                    'EUR': (1 + 1)/2.,
                    'AFR': (2 + 1 + 2 + 2 + 1)/5.
    }
    expected_av_w_degree_by_pop = {
                    'glob': round(((1./10)*2 + (4./10)*3 + (1./10)*1 + (1./10)*2 + (2./10)*3 + (1./10)*1)/6., 4),
                    'AMR': numpy.nan,
                    'ASN': numpy.nan,
                    'EUR': ((1./4)*1 + (3./4)*1)/2.,
                    'AFR': round(((1./6)*2 + (1./6)*1 + (1./6)*2 + (2./6)*2 + (1./6)*1)/5., 4)
    }

class ChromosomeLen7(SimpleNetwork):
#    self.network = GenotypeNetwork(3, 'sample_phenotype')
    name = "chromosome_len_7"
    chromosome_len = 7
#                   EUR           EUR       ASN        AFR         AFR
    genotypes =   ['0010001', '0000110', '0100000', '0000000', '0100000']
    individuals = ['HG1', 'HG2', 'HG3', 'HG4', 'HG5']
    individuals_dict = {
                    'HG1': {'continent': 'EUR', 'subpop': 'TSC', 'phenotype1': 'good'}, 
                    'HG2': {'continent': 'EUR', 'subpop': 'GBR', 'phenotype1': 'bad'}, 
                    'HG3': {'continent': 'ASN', 'subpop': 'AFR', 'phenotype1': 'good'}, 
                    'HG4': {'continent': 'AFR', 'subpop': 'YRI', 'phenotype1': 'good'}, 
                    'HG5': {'continent': 'AFR', 'subpop': 'YRI', 'phenotype1': 'good'}, 
    }

    expected_str_by_pop = {
                    'glob' : "Genotype Network (name = 'chromosome_len_7', chromosome lenght = 7, |V| = 4, |E| = 1)",
                    "AMR": "Genotype Network (name = 'chromosome_len_7_AMR', chromosome lenght = 7, |V| = 0, |E| = 0)",
                    "ASN": "Genotype Network (name = 'chromosome_len_7_ASN', chromosome lenght = 7, |V| = 1, |E| = 0)",
                    "EUR": "Genotype Network (name = 'chromosome_len_7_EUR', chromosome lenght = 7, |V| = 2, |E| = 0)",
                    "AFR": "Genotype Network (name = 'chromosome_len_7_AFR', chromosome lenght = 7, |V| = 2, |E| = 1)",
    }
    expected_report_by_pop = {
                    'glob': "chromosome_len_7 glob 7 5 4 1 3 1 0.1667 1.25 1.0 0.5 1 0.0 0.2917",
                    'AMR': "chromosome_len_7_AMR AMR 7 0 0 0 0 0 nan nan nan nan 0 nan nan",
                    'ASN': "chromosome_len_7_ASN ASN 7 1 1 0 1 0 nan 1.0 nan 0.0 0 0.0 nan",
                    'EUR': "chromosome_len_7_EUR EUR 7 2 2 0 2 0 0.0 1.0 nan 0.0 0 0.0 0.5",
                    'AFR': "chromosome_len_7_AFR AFR 7 2 2 1 1 1 1.0 1.0 1.0 1.0 1 0.0 1.0"
    }
    expected_nodes_by_pop = {
#                    'glob': ['0000000', '0000110', '0010001', '0100000'],
                    'glob': ['0010001', '0000110', '0100000', '0000000'],
                    'AMR': [],
                    'ASN': ['0100000'],
                    'EUR': ['0000110', '0010001'],
                    'AFR': ['0000000', '0100000']
    }

    expected_individuals_by_pop = {
                    'glob': [['HG1'], ['HG2'], ['HG3', 'HG5'], ['HG4']],
                    'AMR': [],
                    'ASN': [['HG3']],
                    'EUR': [['HG1'], ['HG2']],
                    'AFR': [['HG5'], ['HG4']]
    }

    expected_n_datapoints_by_pop = {
                    'glob': [1, 1, 2, 1],
                    'AMR': [],
                    'ASN': [1],
                    'EUR': [1, 1],
                    'AFR': [1, 1]
    }

    expected_diameter_by_pop = {
                    'glob': 1,
                    'AMR': 0,
                    'ASN': 0,
                    'EUR': 0,
                    'AFR': 1
    }
    expected_avdegree_by_pop = {
                    'glob': round((0 + 0 + 1 + 1)/4., 4),
                    'AMR': numpy.nan,
                    'ASN': 0,
                    'EUR': 0,
                    'AFR': 1
    }
    expected_av_w_degree_by_pop = {
                    'glob': round((0 + 0 + (2./5)*1 + (1./5)*1)/4., 4),
                    'AMR': numpy.nan,
                    'ASN': 0,
                    'EUR': 0,
                    'AFR': 1/2.
    }

class OneNode10Individuals(SimpleNetwork):
    name = 'onenode_10inds'
#                    EUR    EUR    AFR    AFR    AFR    AFR    AMR    EUR    AFR    ASN
    genotypes  =   ['000', '000', '000', '000', '000', '000', '000', '000', '000', '000']
    individuals =  ['HG1', 'HG2', 'HG3', 'HG4', 'HG5', 'HG6', 'HG7', 'HG8', 'HG9', 'HG10']
    individuals_dict = {
                     'HG1': {'continent': 'EUR', 'subpop': 'TSC', 'phenotype1': 'good'}, 
                     'HG2': {'continent': 'EUR', 'subpop': 'GBR', 'phenotype1': 'bad'}, 
                     'HG3': {'continent': 'AFR', 'subpop': 'AFR', 'phenotype1': 'good'}, 
                     'HG4': {'continent': 'AFR', 'subpop': 'YRI', 'phenotype1': 'good'}, 
                     'HG5': {'continent': 'AFR', 'subpop': 'YRI', 'phenotype1': 'good'}, 
                     'HG6': {'continent': 'AFR', 'subpop': 'AFR', 'phenotype1': 'good'}, 
                     'HG7': {'continent': 'AMR', 'subpop': 'YRI', 'phenotype1': 'good'}, 
                     'HG8': {'continent': 'EUR', 'subpop': 'YRI', 'phenotype1': 'good'}, 
                     'HG9': {'continent': 'AFR', 'subpop': 'AFR', 'phenotype1': 'good'}, 
                     'HG10': {'continent': 'ASN', 'subpop': 'YRI', 'phenotype1': 'good'}, 
    }
    expected_str_by_pop = {
                    'glob' : "Genotype Network (name = 'onenode_10inds', chromosome lenght = 3, |V| = 1, |E| = 0)",
                    "AMR": "Genotype Network (name = 'onenode_10inds_AMR', chromosome lenght = 3, |V| = 1, |E| = 0)",
                    "ASN": "Genotype Network (name = 'onenode_10inds_ASN', chromosome lenght = 3, |V| = 1, |E| = 0)",
                    "EUR": "Genotype Network (name = 'onenode_10inds_EUR', chromosome lenght = 3, |V| = 1, |E| = 0)",
                    "AFR": "Genotype Network (name = 'onenode_10inds_AFR', chromosome lenght = 3, |V| = 1, |E| = 0)",
    }
    expected_report_by_pop = {
                    'glob': "onenode_10inds glob 3 10 1 0 1 0 nan 10.0 nan 0.0 0 0.0 nan",
                    'AMR': "onenode_10inds_AMR AMR 3 1 1 0 1 0 nan 1.0 nan 0.0 0 0.0 nan",
                    'ASN': "onenode_10inds_ASN ASN 3 1 1 0 1 0 nan 1.0 nan 0.0 0 0.0 nan",
                    'EUR': "onenode_10inds_EUR EUR 3 3 1 0 1 0 nan 3.0 nan 0.0 0 0.0 nan",
                    'AFR': "onenode_10inds_AFR AFR 3 5 1 0 1 0 nan 5.0 nan 0.0 0 0.0 nan"
    }
    expected_nodes_by_pop = {
                     'glob': ['000'],
                     'AMR': ['000'],
                     'ASN': ['000'],
                     'EUR': ['000'],
                     'AFR': ['000']
    }
    expected_individuals_by_pop = {
                    'glob': ['HG1 HG2 HG3 HG4 HG5 HG6 HG7 HG8 HG9 HG10'.split(' ')],
                    'AMR': [['HG7']],
                    'ASN': [['HG10']],
                    'EUR': [['HG1', 'HG2', 'HG8']],
                    'AFR': [['HG3', 'HG4', 'HG5', 'HG6', 'HG9']]
    }
    expected_n_datapoints_by_pop = {
                    'glob': [10],
                    'AMR': [1],
                    'ASN': [1],
                    'EUR': [3],
                    'AFR': [5]
    }
    expected_diameter_by_pop = {
                    'glob': 0,
                    'AMR': 0,
                    'ASN': 0,
                    'EUR': 0,
                    'AFR': 0
    }

    expected_avdegree_by_pop = {
                    'glob': 0,
                    'AMR': 0,
                    'ASN': 0,
                    'EUR': 0,
                    'AFR': 0
    }
    expected_av_w_degree_by_pop = {
                    'glob': 0,
                    'AMR': 0,
                    'ASN': 0,
                    'EUR': 0,
                    'AFR': 0
    }



class Simple_5SNPs_10Inds(SimpleNetwork):
    name = 'simple_5SNPs_10Inds'
#                    EUR    EUR    AFR    AFR    AFR    AFR    AMR    EUR    AFR    ASN
    genotypes  =   ['001', '000', '000', '000', '010', '000', '100', '111', '110', '101']
    individuals =  ['HG1', 'HG2', 'HG3', 'HG4', 'HG5', 'HG6', 'HG7', 'HG8', 'HG9', 'HG10']
    individuals_dict = {
                     'HG1': {'continent': 'EUR', 'subpop': 'TSC', 'phenotype1': 'good'}, 
                     'HG2': {'continent': 'EUR', 'subpop': 'GBR', 'phenotype1': 'bad'}, 
                     'HG3': {'continent': 'AFR', 'subpop': 'AFR', 'phenotype1': 'good'}, 
                     'HG4': {'continent': 'AFR', 'subpop': 'YRI', 'phenotype1': 'good'}, 
                     'HG5': {'continent': 'AFR', 'subpop': 'YRI', 'phenotype1': 'good'}, 
                     'HG6': {'continent': 'AFR', 'subpop': 'AFR', 'phenotype1': 'good'}, 
                     'HG7': {'continent': 'AMR', 'subpop': 'YRI', 'phenotype1': 'good'}, 
                     'HG8': {'continent': 'EUR', 'subpop': 'YRI', 'phenotype1': 'good'}, 
                     'HG9': {'continent': 'AFR', 'subpop': 'AFR', 'phenotype1': 'good'}, 
                     'HG10': {'continent': 'ASN', 'subpop': 'YRI', 'phenotype1': 'good'}, 
    }
    expected_str_by_pop = {
                    'glob' : "Genotype Network (name = 'simple_5SNPs_10Inds', chromosome lenght = 3, |V| = 7, |E| = 9)", 
                    "AMR": "Genotype Network (name = 'simple_5SNPs_10Inds_AMR', chromosome lenght = 3, |V| = 1, |E| = 0)",
                    "ASN": "Genotype Network (name = 'simple_5SNPs_10Inds_ASN', chromosome lenght = 3, |V| = 1, |E| = 0)",
                    "EUR": "Genotype Network (name = 'simple_5SNPs_10Inds_EUR', chromosome lenght = 3, |V| = 3, |E| = 1)",
                    "AFR": "Genotype Network (name = 'simple_5SNPs_10Inds_AFR', chromosome lenght = 3, |V| = 3, |E| = 2)",
    }
    expected_report_by_pop = {
                    'glob': "simple_5SNPs_10Inds glob 3 10 7 9 1 3 0.4286 1.4286 1.7143 2.5714 3 2.1429 0.5861",
                    'AMR': "simple_5SNPs_10Inds_AMR AMR 3 1 1 0 1 0 nan 1.0 nan 0.0 0 0.0 nan",
                    'ASN': "simple_5SNPs_10Inds_ASN ASN 3 1 1 0 1 0 nan 1.0 nan 0.0 0 0.0 nan",
                    'EUR': "simple_5SNPs_10Inds_EUR EUR 3 3 3 1 2 1 0.3333 1.0 1.0 0.6667 1 0.0 0.4444",
                    'AFR': "simple_5SNPs_10Inds_AFR AFR 3 5 3 2 1 2 0.6667 1.6667 1.3333 1.3333 2 0.3333 0.7778"
    }
    expected_nodes_by_pop = {
                     'glob': ['001', '000', '010', '100', '111', '110', '101'],
                     'AMR': ['100'],
                     'ASN': ['101'],
                     'EUR': ['001', '000', '111'],
                     'AFR': ['000', '010', '110']
    }
    expected_individuals_by_pop = {
                    'glob': [['HG1'], 'HG2 HG3 HG4 HG6'.split(' '), ['HG5'], ['HG7'], ['HG8'], ['HG9'], ['HG10']],
                    'AMR': [['HG7']],
                    'ASN': [['HG10']],
                    'EUR': [['HG1'], ['HG2'], ['HG8']],
#                    'EUR': [['HG3', 'HG4', 'HG6'], ['HG2'], ['HG8']],
                    'AFR': [['HG3', 'HG4', 'HG6'], ['HG5'], ['HG9']]
    }
    expected_n_datapoints_by_pop = {
                    'glob': [1, 4, 1, 1, 1, 1, 1],
                    'AMR': [1],
                    'ASN': [1],
                    'EUR': [1, 1, 1],
                    'AFR': [3, 1, 1]
    }
    expected_diameter_by_pop = {
                    'glob': 3,
                    'AMR': 0,
                    'ASN': 0,
                    'EUR': 1,
                    'AFR': 2
    }
    expected_avdegree_by_pop = {
                    'glob': round((2 + 3 + 2 + 3 + 2 + 3 + 3)/7., 4),
                    'AMR': numpy.nan,
                    'ASN': numpy.nan,
                    'EUR': round((1 + 1 + 0)/3., 4),
                    'AFR': round((1 + 2 + 1)/3., 4)
    }
    expected_av_w_degree_by_pop = {
                    'glob': round(((1./10)*2 + (4./10)*3 + (1./10)*2 + (1./10)*3 + (1./10)*2 + (1./10)*3 + (1./10)*3)/7., 4),
                    'AMR': 0,
                    'ASN': 0,
                    'EUR': round(((1./3)+(1./3))/3., 4),
                    'AFR': ((3./5)*1 + (1./5)*2 + (1./5)*1)/ 3.
    }




if __name__ == '__main__':
    import logging
    import doctest
    logging.basicConfig(level=logging.DEBUG)
    doctest.testmod()


