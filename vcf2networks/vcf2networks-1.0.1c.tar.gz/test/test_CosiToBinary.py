#!/usr/bin/env python
"""
"""
#from test_SubgraphByPop import SimpleNetwork
import cosi_to_binary
import unittest
import nose
import subprocess


def test_CosiToBinaryDoctest():
    """
    >>> from cosi_to_binary import read_hap_file
    >>> from tempfile import NamedTemporaryFile
    >>> hapfile = NamedTemporaryFile(delete=False)
    >>> hapfile.write(r'''
    ... 0       1       1 1 2 2 2 1 2 1
    ... 1       1       2 1 2 2 2 1 1 1
    ... 2       1       2 1 2 2 1 2 2 2
    ... 3       1       1 1 2 2 2 1 2 1
    ... 4       1       2 2 1 1 1 1 1 2
    ... 5       1       2 1 1 2 2 1 2 1
    ... 6       1       1 2 2 2 2 1 2 1
    ... 7       1       1 1 1 2 1 1 2 1
    ... ''')

    >>> hapfile.close()

    ===========================
    Example Output binary file
    ===========================
    >>> print (read_hap_file(hapfile.name)) #doctest: +NORMALIZE_WHITESPACE
    #binary file v2. Simulations results. MAF filter: 0.01. Only SNPs that have MAF > 0.01 in each population are kept.
    #number of SNPs: 8. SNPs filtered: 0
    neutral_sim hap0_pop1 pop1 EUR X 0 0 1 1 1 0 1 0
    neutral_sim hap1_pop1 pop1 EUR X 1 0 1 1 1 0 0 0
    neutral_sim hap2_pop1 pop1 EUR X 1 0 1 1 0 1 1 1
    neutral_sim hap3_pop1 pop1 EUR X 0 0 1 1 1 0 1 0
    neutral_sim hap4_pop1 pop1 EUR X 1 1 0 0 0 0 0 1
    neutral_sim hap5_pop1 pop1 EUR X 1 0 0 1 1 0 1 0
    neutral_sim hap6_pop1 pop1 EUR X 0 1 1 1 1 0 1 0
    neutral_sim hap7_pop1 pop1 EUR X 0 0 0 1 0 0 1 0
    <BLANKLINE>

    """

def test_GlobalPopFile():
    """
    parse a COSI file containing 3 populations.
    
    >>> from cosi_to_binary import read_hap_file
    >>> from tempfile import NamedTemporaryFile
    >>> hapfile2 = NamedTemporaryFile(prefix='hap2', delete=False)
    >>> hapfile2.write(r'''0       1       2 1 2 2 2 
    ... 1       1       2 1 1 1 2
    ... 2       1       2 1 2 2 1
    ... 3       2       2 1 1 1 1
    ... 4       2       2 1 2 2 2
    ... 5       2       2 1 1 1 1
    ... 6       3       2 1 1 2 2
    ... 7       3       2 1 2 1 1
    ... 8       3       2 1 1 1 2
    ... ''')
    >>> hapfile2.close()


    >>> print (read_hap_file(hapfile2.name))  #doctest: +NORMALIZE_WHITESPACE
    #binary file v2. Simulations results. MAF filter: 0.01. Only SNPs that have MAF > 0.01 in each population are kept.
    #number of SNPs: 5. SNPs filtered: 2
    neutral_sim hap0_pop1 pop1 EUR X 1 1 1
    neutral_sim hap1_pop1 pop1 EUR X 0 0 1
    neutral_sim hap2_pop1 pop1 EUR X 1 1 0
    neutral_sim hap0_pop3 pop3 AFR X 0 1 1
    neutral_sim hap1_pop3 pop3 AFR X 1 0 0
    neutral_sim hap2_pop3 pop3 AFR X 0 0 1
    neutral_sim hap0_pop2 pop2 ASN X 0 0 0
    neutral_sim hap1_pop2 pop2 ASN X 1 1 1
    neutral_sim hap2_pop2 pop2 ASN X 0 0 0
    <BLANKLINE>

    >>> hapfile2.unlink(hapfile2.name)
    """

def test_GlobalPopFileAssymetric():
    """
    parse a COSI file containing 3 populations, where one population contains an homorphic SNP.
    
    >>> from cosi_to_binary import read_hap_file
    >>> from tempfile import NamedTemporaryFile
    >>> hapfile2 = NamedTemporaryFile(prefix='hap2', delete=False)
    >>> hapfile2.write(r'''0       1       2 1 2 2 2 
    ... 1       1       2 1 1 1 2
    ... 2       1       2 1 2 2 1
    ... 3       2       2 1 1 1 1
    ... 4       2       2 1 2 2 2
    ... 5       2       2 1 1 1 1
    ... 6       3       2 1 1 2 2
    ... 7       3       2 1 2 1 2
    ... 8       3       2 1 1 1 2
    ... ''')
    >>> hapfile2.close()


    >>> print (read_hap_file(hapfile2.name))  #doctest: +NORMALIZE_WHITESPACE
    #binary file v2. Simulations results. MAF filter: 0.01. Only SNPs that have MAF > 0.01 in each population are kept.
    #number of SNPs: 5. SNPs filtered: 3
    neutral_sim hap0_pop1 pop1 EUR X 1 1
    neutral_sim hap1_pop1 pop1 EUR X 0 0
    neutral_sim hap2_pop1 pop1 EUR X 1 1
    neutral_sim hap0_pop3 pop3 AFR X 0 1
    neutral_sim hap1_pop3 pop3 AFR X 1 0
    neutral_sim hap2_pop3 pop3 AFR X 0 0
    neutral_sim hap0_pop2 pop2 ASN X 0 0
    neutral_sim hap1_pop2 pop2 ASN X 1 1
    neutral_sim hap2_pop2 pop2 ASN X 0 0
    <BLANKLINE>

    >>> hapfile2.unlink(hapfile2.name)
    """




class ShortCosiSimulation(unittest.TestCase):
    hapfile = 'test/test_data/simulations/cosiout_short.hap-1'

    # number of snps == number of rows the input file, minus those filtered by MAF
    expected_number_snps = 30

    # number of chromosomes == number of columns in input file
    # in this case, the short cosi sim file has been generating by taking the first 49 columns
    expected_number_chromosomes = 120

    def setUp(self):
        self.binary_output = cosi_to_binary.read_hap_file(self.hapfile, maf_filter=0.01)
        self.binaryoutput_lines = self.binary_output.split('\n')

    def test_NumberSnps(self):
#        print self.binaryoutput_lines[0].split()[2:]
        n_snps = len(self.binaryoutput_lines[0].split()[5:])
#        assert False
#        n_snps = len(self.binaryoutput_lines[0][17:]) / 2
        nose.tools.assert_equal(n_snps, self.expected_number_snps)
    
    def test_NumberChromosomes(self):
        n_chromosomes = len([line for line in self.binaryoutput_lines if line.startswith('neutral_sim')])
        nose.tools.assert_equal(n_chromosomes, self.expected_number_chromosomes)



#class MonomorphicCosiSimulation(ShortCosiSimulation):
#    """
#    A cosi simulation where all the SNPs are monomorphic.
#    """


@nose.plugins.attrib.attr('slow')
class LongCosiSimulation(ShortCosiSimulation):
    """
    like ShortCosiSimulation, but takes longer
    """
    hapfile = 'test/test_data/simulations/cosiout_long.hap-1'

    # number of snps == number of rows the input file, minus those filtered by MAF
    expected_number_snps = 2803

    # number of chromosomes == number of columns in input file
    expected_number_chromosomes = 120

@nose.plugins.attrib.attr('slow')
class GzippedCosiSimulation(ShortCosiSimulation):
    """
    like ShortCosiSimulation, but takes longer
    """
    hapfile = 'test/test_data/simulations/bestfit_neutral_replica_1.hap-1.gz'

    # number of snps == number of rows the input file, minus those filtered by MAF
    expected_number_snps = 936

    # number of chromosomes == number of columns in input file
    expected_number_chromosomes = 120


def test_CommandLineCosiToBin():
    "Try to call cosi_to_binary.py, and check the first output line."
    import subprocess 
    output = subprocess.check_output("python src/cosi_to_binary.py -m 0.05 -f test/test_data/simulations/cosiout_short.hap-1".split())
    expected_firstline = "neutral_sim hap0_pop1 pop1 EUR X 1 1 1 1 1 1 1 1 1 1 1 1 1"
    firstline = output.split('\n')[2]
#    nose.tools.assert_sequence_equal(firstline, expected_firstline)
    nose.tools.assert_equal(firstline, expected_firstline)
       
def test_CommandLineCosiToBinMafFilter010():
    "Try to call cosi_to_binary.py, using a MAF filter 0.10, and check the first output line."
    import subprocess 
    output = subprocess.check_output("python src/cosi_to_binary.py -f test/test_data/simulations/cosiout_short.hap-1 -m 0.10".split())
    expected_firstline = "neutral_sim hap0_pop1 pop1 EUR X 1 1 1 1 1 1"
    firstline = output.split('\n')[2]
#    nose.tools.assert_sequence_equal(firstline, expected_firstline)
    nose.tools.assert_equals(firstline, expected_firstline)
    
if __name__ == '__main__':
    import logging
    import doctest
    logging.basicConfig(level=logging.DEBUG)
    doctest.testmod()


