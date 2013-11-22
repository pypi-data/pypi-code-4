#!/usr/bin/env python
"""
"""
import unittest
import nose
from GenotypeNetwork import GenotypeNetworkInitError

@nose.plugins.attrib.attr("nocluster")
class Simple_5SNPs_5Inds_Network(unittest.TestCase):
    def setUp(self):
        from GenotypeNetwork import GenotypeNetwork
        self.network = GenotypeNetwork(5, 'sample_phenotype')
        self.genotypes = ['00001', '01000', '00000', '01001', '01101']
        self.network.populate_from_binary_strings(self.genotypes)

    def test_summary(self):
        print "PRINT", self.network.summary()
        expected_output = "5 nodes, 5 edges, undirected\n\nNumber of components: 1\nDiameter: 3\nDensity: 0.5000\nAverage path length: 1.6000"

        output = self.network.summary()
        print output
        self.assertEqual(output, expected_output)


@nose.plugins.attrib.attr("nocluster")
def test_GoodGenotypes():
    """
    Test different types of valid inputs for GenotypeNetwork, they should all work without errors
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

@nose.plugins.attrib.attr("nocluster")
def test_WrongGenotypes():
    """
    Test different types of wrong inputs for GenotypeNetwork, they should all return errors
    """
    wrong_genotypes = [
        (3, ['001', '000', '020'], ""),         # contains a "2"
        (2, ['001', '000', '010'], ""),         # wrong chromosome_len
        (3, ['001', '000', '00'], ""),          # wrong length
        (5, ['00101', '11000', '0000'], ""),    # wrong length
        (3, '001', ''),                         # genotypes is not a list
        ]

    for params_set in wrong_genotypes: 
        yield check_WrongGenotypesError, params_set[0], params_set[1], params_set[2]

@nose.tools.raises(GenotypeNetworkInitError)
def check_WrongGenotypesError(chromosome_len, genotypes, expectederrormessage):
    from GenotypeNetwork import GenotypeNetwork
    print chromosome_len, genotypes
    net = GenotypeNetwork(chromosome_len, genotypes=genotypes)
    print genotypes


if __name__ == '__main__':
    import logging
    import doctest
    logging.basicConfig(level=logging.DEBUG)
    doctest.testmod()


