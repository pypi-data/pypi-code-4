#!/usr/bin/env python
"""
"""
import unittest
import nose
import GenotypeNetwork
import binary_to_network

testfiles = [
    "test/test_data/MOGS.binary"
   ]

pickledir = 'test/test_data/pickles/'

class MOGS(unittest.TestCase):
    gene_name = 'MOGS'
    binary_genotypes_file = 'test/test_data/binary_genotypes/{0}.binary'.format(gene_name)
    graphml_file = 'test/test_data/graphml/MOGS.graphml'
    individuals_file = 'test/test_data/phase1_integrated_calls.20101123.ALL.panel.individuals'

#    def __init__(self, gene_name):
#        self.gene_name = gene_name
#        self.binary_genotypes_file = 'test/test_data/{}.binary'.format(self.gene_name)
#
    def setUp(self): # TODO: see if you can use setUpAll
        self.individuals_dict = binary_to_network.parse_individuals_file(self.individuals_file, pickle_from_file_if_possible=False) #TODO: de-activate pickling of this variable

        self.all_genotypes, self.individuals, self.individuals_dict, self.gene_name = binary_to_network.parse_binary_file(
                    self.binary_genotypes_file, self.individuals_dict)
        self.binary_network = binary_to_network.generate_network(self.all_genotypes, self.individuals, self.individuals_dict, self.gene_name) 
        
        self.binary_network.write_graphml(self.graphml_file)
        self.graphml_network = GenotypeNetwork.network_from_file(self.graphml_file)
        print self.graphml_network

    def test_NumberVertices(self):
        assert(self.binary_network.vcount() == self.graphml_network.vcount())

    def test_NumberEdges(self):
        assert(self.binary_network.ecount() == self.graphml_network.ecount())

    def test_VertexAttributes(self):
        print(self.binary_network.vertex_attributes(), self.graphml_network.vertex_attributes())
        print self.graphml_network.vs['id']
#        assert False
        assert([(att in self.graphml_network.vertex_attributes()) for att in  self.binary_network.vertex_attributes()])

    def test_NetworkAttributes(self):
        print(self.binary_network.attributes(), self.graphml_network.attributes())
        print self.graphml_network.vs['id']
#        assert False
        assert([(att in self.graphml_network.attributes()) for att in  self.binary_network.attributes()])

    def test_VertexGenotypes(self):
        assert(self.binary_network.vs['genotype'] == self.graphml_network.vs['genotype'])

    def test_Str(self):
        print(self.binary_network.__str__(), self.graphml_network.__str__())
        assert(self.binary_network.__str__() == self.graphml_network.__str__())

    def test_CsvReport(self):
        print(self.binary_network.csv_report(), self.graphml_network.csv_report())
        assert(self.binary_network.csv_report() == self.graphml_network.csv_report())

class ALG3(MOGS):
    """
    """
    gene_name = 'ALG3'
    binary_genotypes_file = 'test/test_data/binary_genotypes/{0}.binary'.format(gene_name)

#def test_ALG13
#    The ALG13 gene contains some 2, so it should return errors

@nose.plugins.attrib.attr('slow')
class RPN2(MOGS):
    gene_name = 'RPN2'
    binary_genotypes_file = 'test/test_data/binary_genotypes/{0}.binary'.format(gene_name)


if __name__ == '__main__':
    import logging
    import doctest
    logging.basicConfig(level=logging.DEBUG)
    doctest.testmod()


