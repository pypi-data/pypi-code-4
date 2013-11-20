#!/usr/bin/env python
"""
Test the GenotypeNetwork.populate_from_binary_strings and populate_from_binary_strings_and_individuals functions, using different distance values
"""
import unittest
import nose

@nose.plugins.attrib.attr("nocluster")
class Simple_5SNPs_Network(unittest.TestCase):
    """Simple 5 SNPs, 10 individuals network

    This network should have 2 components if distance==1, and 1 if distance==2 or distance==3
    """
    genotypes = ['00000', '00000', '00000', '00000', '11000', '11000', '11000', '11000', '00011', '00011']
    chromosome_len = 5

    expected_distance_1_summary = "3 nodes, 0 edges, undirected\n\nNumber of components: 3\nDiameter: 0\nDensity: 0.0000\nAverage path length: nan"
    expected_distance_2_summary = "3 nodes, 2 edges, undirected\n\nNumber of components: 1\nDiameter: 2\nDensity: 0.6667\nAverage path length: 1.3333"
    expected_distance_3_summary = "3 nodes, 2 edges, undirected\n\nNumber of components: 1\nDiameter: 2\nDensity: 0.6667\nAverage path length: 1.3333"

    expected_distance_1_ncomponents = 3
    expected_distance_2_ncomponents = 1    
    expected_distance_3_ncomponents = 1    

    def setUp(self):
        from GenotypeNetwork import GenotypeNetwork

        self.network_distance_1 = GenotypeNetwork(self.chromosome_len, 'Distance==1 network')
        self.network_distance_1.populate_from_binary_strings(self.genotypes, distance=1)
        
        self.network_distance_2 = GenotypeNetwork(self.chromosome_len, 'Distance==2 network')
        self.network_distance_2.populate_from_binary_strings(self.genotypes, distance=2)

        self.network_distance_3 = GenotypeNetwork(self.chromosome_len, 'Distance==3 network')
        self.network_distance_3.populate_from_binary_strings(self.genotypes, distance=3)

    def test_Distance_1_Summary(self):
        print [vertex['genotype'] for vertex in self.network_distance_1.vs()]
        print [edge.tuple for edge in self.network_distance_1.es()]
#        nose.tools.assert_sequence_equal(self.expected_distance_1_summary, self.network_distance_1.summary())
        nose.tools.assert_equals(self.expected_distance_1_summary, self.network_distance_1.summary())

    def test_Distance_2_Summary(self):
        print [vertex['genotype'] for vertex in self.network_distance_2.vs()]
        print [edge.tuple for edge in self.network_distance_2.es()]
#        nose.tools.assert_sequence_equal(self.expected_distance_2_summary, self.network_distance_2.summary())
        nose.tools.assert_equals(self.expected_distance_2_summary, self.network_distance_2.summary())

    def test_Distance_3_Summary(self):
        print [vertex['genotype'] for vertex in self.network_distance_3.vs()]
        print [edge.tuple for edge in self.network_distance_3.es()]
#        nose.tools.assert_sequence_equal(self.expected_distance_3_summary, self.network_distance_3.summary())
        nose.tools.assert_equals(self.expected_distance_3_summary, self.network_distance_3.summary())

    def test_Distance_1_NComponents(self):
        nose.tools.assert_equal(self.expected_distance_1_ncomponents, len(self.network_distance_1.components()))

    def test_Distance_2_NComponents(self):
        nose.tools.assert_equal(self.expected_distance_2_ncomponents, len(self.network_distance_2.components()))

    def test_Distance_3_NComponents(self):
        nose.tools.assert_equal(self.expected_distance_3_ncomponents, len(self.network_distance_3.components()))


@nose.plugins.attrib.attr("nocluster")
class Simple_OneNode_Network(Simple_5SNPs_Network):
    """
    One node network. All networks should be the same, regardless of the distance attribute.
    """
    genotypes = ['00000', '00000', '00000', '00000', '00000', '00000', '00000', '00000', '00000', '00000']
    chromosome_len = 5

    expected_distance_1_summary = "1 nodes, 0 edges, undirected\n\nNumber of components: 1\nDiameter: 0\nDensity: nan\nAverage path length: nan"
    expected_distance_2_summary = "1 nodes, 0 edges, undirected\n\nNumber of components: 1\nDiameter: 0\nDensity: nan\nAverage path length: nan"
    expected_distance_3_summary = "1 nodes, 0 edges, undirected\n\nNumber of components: 1\nDiameter: 0\nDensity: nan\nAverage path length: nan"

    expected_distance_1_ncomponents = 1
    expected_distance_2_ncomponents = 1    
    expected_distance_3_ncomponents = 1    

@nose.plugins.attrib.attr("nocluster")
class BiggerNetwork1(Simple_5SNPs_Network):
    """
    Three Nodes Network.  This is bigger example than the others and attributes are only checked manually.
    """
    genotypes = ['00001', '10000', '01000', '00010', '00100', '01000', '00010', '11111', '00010', '01100']
    chromosome_len = 5

    expected_distance_1_summary = "7 nodes, 2 edges, undirected\n\nNumber of components: 5\nDiameter: 2\nDensity: 0.0952\nAverage path length: 1.3333"
    expected_distance_2_summary = "7 nodes, 12 edges, undirected\n\nNumber of components: 2\nDiameter: 2\nDensity: 0.5714\nAverage path length: 1.2000"
    expected_distance_3_summary = "7 nodes, 16 edges, undirected\n\nNumber of components: 1\nDiameter: 2\nDensity: 0.7619\nAverage path length: 1.2381"

    expected_distance_1_ncomponents = 5
    expected_distance_2_ncomponents = 2    
    expected_distance_3_ncomponents = 1    

@nose.plugins.attrib.attr("nocluster")
class BiggerRandomNetwork(Simple_5SNPs_Network):
    """
    Network generated randomly. 100 nodes, 10 SNPs

    """
    genotypes = ['00001', '10000', '01000', '00010', '00100', '01000', '00010', '11111', '00010', '01100']
    chromosome_len = 10

    expected_distance_1_summary = "95 nodes, 28 edges, undirected\n\nNumber of components: 67\nDiameter: 7\nDensity: 0.0063\nAverage path length: 2.4267"
    expected_distance_2_summary = "95 nodes, 234 edges, undirected\n\nNumber of components: 2\nDiameter: 8\nDensity: 0.0524\nAverage path length: 3.5228"
    expected_distance_3_summary = "95 nodes, 732 edges, undirected\n\nNumber of components: 1\nDiameter: 4\nDensity: 0.1639\nAverage path length: 2.0858"

    expected_distance_1_ncomponents = 67
    expected_distance_2_ncomponents = 2    
    expected_distance_3_ncomponents = 1    

    def setUp(self):
        from GenotypeNetwork import GenotypeNetwork
        import random
        random.seed(0)
        self.genotypes = [''.join(str(random.choice((0, 1))) for pos in range(10)) for n_individual in range(100)]

        self.network_distance_1 = GenotypeNetwork(self.chromosome_len, 'Distance==1 network')
        self.network_distance_1.populate_from_binary_strings(self.genotypes, distance=1)
        
        self.network_distance_2 = GenotypeNetwork(self.chromosome_len, 'Distance==2 network')
        self.network_distance_2.populate_from_binary_strings(self.genotypes, distance=2)

        self.network_distance_3 = GenotypeNetwork(self.chromosome_len, 'Distance==3 network')
        self.network_distance_3.populate_from_binary_strings(self.genotypes, distance=3)

@nose.plugins.attrib.attr("nocluster")
class SimpleNetwork_Individuals(Simple_5SNPs_Network):
    chromosome_len = 3
#                   EUR    EUR    AFR    AFR    AFR
    genotypes =   ['101', '000', '000', '111', '110']
    individuals = ['HG1', 'HG2', 'HG3', 'HG4', 'HG5']
    individuals_dict = {
                    'HG1': {'continent': 'EUR', 'subpop': 'TSC', 'phenotype1': 'good'}, 
                    'HG2': {'continent': 'EUR', 'subpop': 'GBR', 'phenotype1': 'bad'}, 
                    'HG3': {'continent': 'AFR', 'subpop': 'AFR', 'phenotype1': 'good'}, 
                    'HG4': {'continent': 'AFR', 'subpop': 'YRI', 'phenotype1': 'good'}, 
                    'HG5': {'continent': 'AFR', 'subpop': 'YRI', 'phenotype1': 'good'}, 
    }
    expected_distance_1_summary = "4 nodes, 2 edges, undirected\n\nNumber of components: 2\nDiameter: 2\nDensity: 0.3333\nAverage path length: 1.3333"
    expected_distance_2_summary = "4 nodes, 5 edges, undirected\n\nNumber of components: 1\nDiameter: 2\nDensity: 0.8333\nAverage path length: 1.1667"
    expected_distance_3_summary = "4 nodes, 6 edges, undirected\n\nNumber of components: 1\nDiameter: 1\nDensity: 1.0000\nAverage path length: 1.0000"

    expected_distance_1_ncomponents = 2
    expected_distance_2_ncomponents = 1    
    expected_distance_3_ncomponents = 1    

    def setUp(self):
        from GenotypeNetwork import GenotypeNetwork

        self.network_distance_1 = GenotypeNetwork(self.chromosome_len, 'Distance==1 network')
        self.network_distance_1.populate_from_binary_strings_and_individuals(self.genotypes, distance=1, individuals=self.individuals, individuals_dict=self.individuals_dict)
        
        self.network_distance_2 = GenotypeNetwork(self.chromosome_len, 'Distance==2 network')
        self.network_distance_2.populate_from_binary_strings_and_individuals(self.genotypes, distance=2, individuals=self.individuals, individuals_dict=self.individuals_dict)

        self.network_distance_3 = GenotypeNetwork(self.chromosome_len, 'Distance==3 network')
        self.network_distance_3.populate_from_binary_strings_and_individuals(self.genotypes, distance=3, individuals=self.individuals, individuals_dict=self.individuals_dict)




if __name__ == '__main__':
    import logging
    import doctest
    logging.basicConfig(level=logging.DEBUG)
    doctest.testmod()


