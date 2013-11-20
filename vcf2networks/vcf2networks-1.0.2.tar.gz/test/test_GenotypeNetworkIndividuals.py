#!/usr/bin/env python
"""
Check that creating a network with or without specifying individuals leads to the same network
"""
import unittest
import nose
from GenotypeNetwork import GenotypeNetwork

class SimpleNetwork(unittest.TestCase):
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

    def setUp(self): # TODO: see if you can use setUpAll
        self.network_with_individuals = GenotypeNetwork(self.chromosome_len, name = self.name)
        self.network_with_individuals.populate_from_binary_strings_and_individuals(genotypes=self.genotypes, individuals=self.individuals, 
                                individuals_dict=self.individuals_dict)

        self.network_without_individuals = GenotypeNetwork(self.chromosome_len, name = self.name)
        self.network_without_individuals.populate_from_binary_strings(genotypes=self.genotypes)

    def test_individuals(self):
#        nose.tools.assert_sequence_equal(self.network_with_individuals['individuals'], self.individuals)
        nose.tools.assert_equal(self.network_with_individuals['individuals'], self.individuals)

    def test_summary(self):
#        nose.tools.assert_sequence_equal(self.network_with_individuals.summary(), self.network_without_individuals.summary())
        nose.tools.assert_equals(self.network_with_individuals.summary(), self.network_without_individuals.summary())

    def test_csv_report(self):
#        nose.tools.assert_sequence_equal(self.network_with_individuals.csv_report(), self.network_without_individuals.csv_report())
        nose.tools.assert_equals(self.network_with_individuals.csv_report(), self.network_without_individuals.csv_report())

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


if __name__ == '__main__':
    import logging
    import doctest
    logging.basicConfig(level=logging.DEBUG)
    doctest.testmod()


