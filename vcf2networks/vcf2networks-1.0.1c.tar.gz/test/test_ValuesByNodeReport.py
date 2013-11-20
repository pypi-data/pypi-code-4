#!/usr/bin/env python
"""
"""
import unittest
import nose
from GenotypeNetwork import GenotypeNetworkInitError, GenotypeNetworkAttributeError

class Simple_5SNPs_Network(unittest.TestCase):
    
    chromosome_len = 5
    name = 'sample_phenotype'
    genotypes = ['00001', '01000', '00000', '01001', '01101']

    # expected values
    expected_summary = "5 nodes, 5 edges, undirected\n\nNumber of components: 1\nDiameter: 3\nDensity: 0.5000\nAverage path length: 1.6000"
#    expected_nodes = ['00000', '00001', '01000', '01001', '01101']
    expected_nodes = ['01101', '00001', '00000', '01000', '01001']
    expected_degree = [1, 2, 2, 2, 3]
    expected_max_closeness = '01001'
    expected_closeness = [0.5, 0.6667, 0.5714, 0.6667, 0.8]

    def setUp(self):
        from GenotypeNetwork import GenotypeNetwork
        self.network = GenotypeNetwork(self.chromosome_len, self.name)
        self.network.populate_from_binary_strings(self.genotypes)
    
    def test_summary(self):
        print "PRINT", self.network.summary()

        output = self.network.summary()
        print output
        self.assertEqual(output, self.expected_summary)

    def test_SimpleDegreeClosenessReport(self):
        tested_attributes = ['genotype', 'degree', 'closeness']
        expected_degree_report = reproduce_valuesBySnp_output(tested_attributes, [self.expected_nodes, self.expected_degree, self.expected_closeness])
        print expected_degree_report
#        nose.tools.assert_sequence_equal(expected_degree_report, self.network.values_by_node(tested_attributes))
        nose.tools.assert_equals(expected_degree_report, self.network.values_by_node(tested_attributes))

    def test_NetworkNameReport(self):
        tested_attributes = ['genotype', 'name']
        self.expected_name = [self.name] * len(self.genotypes)
        expected_degree_report = reproduce_valuesBySnp_output(tested_attributes, [self.expected_nodes, self.expected_name])
        print expected_degree_report
#        nose.tools.assert_sequence_equal(expected_degree_report, self.network.values_by_node(tested_attributes))
        nose.tools.assert_equals(expected_degree_report, self.network.values_by_node(tested_attributes))

    def test_SimpleDegreeReport(self):
        tested_attributes = ['genotype', 'degree']
        expected_degree_report = reproduce_valuesBySnp_output(tested_attributes, [self.expected_nodes, self.expected_degree])
#        nose.tools.assert_sequence_equal(expected_degree_report, self.network.values_by_node(tested_attributes))
        nose.tools.assert_equals(expected_degree_report, self.network.values_by_node(tested_attributes))


    @nose.tools.raises(GenotypeNetworkAttributeError)
    def test_InexistentAttribute(self):
        tested_attributes = ['genotype', 'basdadas']
#        expected_degree_report = reproduce_valuesBySnp_output(tested_attributes, [self.expected_nodes, self.expected_degree])
#        print expected_degree_report
        self.network.values_by_node(tested_attributes)

class Simple_5SNPs_5Inds_Network(Simple_5SNPs_Network):
    
    chromosome_len = 5
    name = 'sample_phenotype'
    genotypes =   ['00001',    '00000',   '00000',   '00001',   '00010',   '00100',   '00001',   '00001',   '00010',   '00001']
    individuals = ['HG1_1', 'HG1_2', 'HG2_1', 'HG2_2', 'HG3_1', 'HG3_2', 'HG4_1', 'HG4_2', 'HG5_1', 'HG5_2']
    individuals_dict = {
                    'HG1': {'continent': 'EUR', 'subpop': 'TSC', 'phenotype1': 'good'}, 
                    'HG2': {'continent': 'EUR', 'subpop': 'GBR', 'phenotype1': 'bad'}, 
                    'HG3': {'continent': 'AFR', 'subpop': 'AFR', 'phenotype1': 'good'}, 
                    'HG4': {'continent': 'AFR', 'subpop': 'YRI', 'phenotype1': 'good'}, 
                    'HG5': {'continent': 'AFR', 'subpop': 'YRI', 'phenotype1': 'good'}, 
    }


    # expected values
    expected_summary = "4 nodes, 3 edges, undirected\n\nNumber of components: 1\nDiameter: 2\nDensity: 0.5000\nAverage path length: 1.5000"
#    expected_nodes = ['00000', '00001', '01000', '01001', '01101']
    expected_nodes = ['00100', '00001', '00000', '00010']
    expected_degree = [1, 1, 3, 1]
    expected_max_closeness = '00000'
    expected_closeness = [0.6, 0.6, 1.0, 0.6]

    def setUp(self):
        from GenotypeNetwork import GenotypeNetwork
        self.network = GenotypeNetwork(self.chromosome_len, self.name)
        self.network.populate_from_binary_strings(self.genotypes)



def reproduce_valuesBySnp_output(values_names, expected_values):
    """
    Utility function, used for tests only, to reproduce what the output of 
    GenotypeNetwork.values_by_snp should look like, given a list of expected
    values.

    expected_values should be a list of lists of expected values per node.
    Example: 

    >>> reproduce_valuesBySnp_output(values_names=['genotype', 'degree'], 
    ...                 expected_values=['001', '000'], [1, 2]) #doctest: +IGNORE_WHITESPACE
    #genotype   degree
    001 1
    000 2

    See test_reproduceValuesBySnp for example and tests on this function.
    """
    output = '#' + '\t'.join(values_names) + '\n'
    for line_attrs in zip(*expected_values):
        output += '\t'.join([str(att) for att in line_attrs]) + '\n'
    return output[:-1]



def test_reproduceValuesBySnp():
    """
    >>> import GenotypeNetwork
    >>> network = GenotypeNetwork.GenotypeNetwork(3, genotypes = ['001', '000', '000'])
    >>> expected_nodes = ['001', '000']
    >>> [v['genotype'] for v in network.vs] == expected_nodes
    True
    >>> expected_degrees = [1, 1]
    >>> reproduced_output = reproduce_valuesBySnp_output(values_names=['genotype', 'degree'],
    ...             expected_values=[expected_nodes, expected_degrees])  #doctest: +NORMALIZE_WHITESPACE
    >>> print reproduced_output #doctest: +NORMALIZE_WHITESPACE
    #genotype   degree
    001 1
    000 1

    """
#    >>> assert(reproduced_output == "#genotype\tdegree\n001\t1\n000\t1")  #doctest: +NORMALIZE_WHITESPACE
#    True
    pass

def test_GoodParameters():
    """
    Test different types of valid inputs for GenotypeNetwork, and check if they can print a
    values_by_node report, with the default values, without returning errors.
    """
    good_genotypes = [
        (3, ['001', '000', '010'], ""),
        (1, ['1', '0', '0'], ""),
        (4, ['0001', '0010', '1010'], ""),
        (3, ['000', '000', '000'], ""),
        (5, ['00001', '11000', '01110'], ""),
        (3, ['111', '100', '010'], ""),
        ]
    for params_set in good_genotypes:
        yield check_GoodGenotypes, params_set[0], params_set[1], params_set[2]


def check_GoodGenotypes(chromosome_len, genotypes, expectedoutput):
    from GenotypeNetwork import GenotypeNetwork
    net = GenotypeNetwork(chromosome_len, genotypes=genotypes)
    net.values_by_node()

#def test_WrongGenotypes():
#   """
#   Test different types of wrong inputs for GenotypeNetwork, they should all return errors
#   """
#   wrong_genotypes = [
#       (3, ['001', '000', '020'], ""),         # contains a "2"
#       (2, ['001', '000', '010'], ""),         # wrong chromosome_len
#       (3, ['001', '000', '00'], ""),          # wrong length
#       (5, ['00101', '11000', '0000'], ""),    # wrong length
#       (3, '001', ''),                         # genotypes is not a list
#       ]
#
#   for params_set in wrong_genotypes: 
#       yield check_WrongGenotypesError, params_set[0], params_set[1], params_set[2]
#
#@nose.tools.raises(GenotypeNetworkInitError)
#def check_WrongGenotypesError(chromosome_len, genotypes, expectederrormessage):
#   from GenotypeNetwork import GenotypeNetwork
#   print chromosome_len, genotypes
#   net = GenotypeNetwork(chromosome_len, genotypes=genotypes)
#   print genotypes
#

if __name__ == '__main__':
    import logging
    import doctest
    logging.basicConfig(level=logging.DEBUG)
    doctest.testmod()


