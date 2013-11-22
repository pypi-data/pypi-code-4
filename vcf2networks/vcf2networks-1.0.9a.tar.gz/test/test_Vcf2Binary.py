#!/usr/bin/env python
"""
"""
#from test_SubgraphByPop import SimpleNetwork
from filteredvcf_to_binary import *
import unittest
import nose
import subprocess
from tempfile import NamedTemporaryFile



class TestSimpleVCF(unittest.TestCase):
    """
    A simple VCF file
    """
    sample_vcf = r'''#
#CHROM  POS     ID      REF     ALT     QUAL    FILTER  INFO    FORMAT  HG00096 HG00097 HG00099 HG00100 HG00101
14      23033832        rs186383615     T       C       100     PASS    LDAF=0.0016;THETA=0.0004;AA=T;AN=2184;VT=SNP;SNPSOURCE=LOWCOV;ERATE=0.0003;RSQ=0.8538;AVGPOST=0.9995;AC=3;AF=0.0014;AFR_AF=0.0020;EUR_AF=0.0026 GT:DS:GL        1|0:0.000:-0.01,-1.48,-5.00     0|0:0.000:0.00,-5.00,-5.00      0|0:0.000:-0.00,-3.36,-5.00     0|1:0.000:-0.00,-3.19,-5.00     0|0:0.000:-0.00,-4.22,-5.00
14      23033840        rs1051189       G       A       100     PASS    RSQ=0.9958;AC=248;THETA=0.0004;AA=G;AN=2184;AVGPOST=0.9990;VT=SNP;LDAF=0.1138;SNPSOURCE=LOWCOV;ERATE=0.0003;AF=0.11;ASN_AF=0.15;AMR_AF=0.07;AFR_AF=0.13;EUR_AF=0.10     GT:DS:GL        0|0:0.000:-0.01,-1.77,-5.00     0|0:0.000:0.00,-5.00,-5.00      0|1:0.000:-0.00,-2.31,-5.00     0|0:0.000:-0.00,-3.19,-5.00     1|0:0.000:-0.00,-2.31,-5.00
14      23033854        rs1051190       C       G       100     PASS    RSQ=0.9958;AC=248;THETA=0.0004;AA=G;AN=2184;AVGPOST=0.9990;VT=SNP;LDAF=0.1138;SNPSOURCE=LOWCOV;ERATE=0.0003;AF=0.11;ASN_AF=0.15;AMR_AF=0.07;AFR_AF=0.13;EUR_AF=0.10     GT:DS:GL        0|0:0.000:-0.01,-1.77,-5.00     1|0:0.000:0.00,-5.00,-5.00      0|0:0.000:-0.00,-2.31,-5.00     0|1:0.000:-0.00,-3.19,-5.00     1|1:0.000:-0.00,-2.31,-5.00
14      23033888        rs1051191       G       A       100     PASS    RSQ=0.9958;AC=248;THETA=0.0004;AA=G;AN=2184;AVGPOST=0.9990;VT=SNP;LDAF=0.1138;SNPSOURCE=LOWCOV;ERATE=0.0003;AF=0.11;ASN_AF=0.15;AMR_AF=0.07;AFR_AF=0.13;EUR_AF=0.10     GT:DS:GL        0|0:0.000:-0.01,-1.77,-5.00     1|0:0.000:0.00,-5.00,-5.00      0|0:0.000:-0.00,-2.31,-5.00     1|0:0.000:-0.00,-3.19,-5.00     1|0:0.000:-0.00,-2.31,-5.00
'''
    expected_pos_annotations = "23033832 23033840 23033854 23033888".split()
    expected_snp_ids = sorted("rs186383615 rs1051189 rs1051190 rs1051191".split())

    def setUp(self):
        self.vcf_file = NamedTemporaryFile(delete=False)
        self.vcf_file.write(self.sample_vcf)
        self.vcf_file.close()
        (self.indv_annotations, self.genotypes_h5, self.unphased_genotypes_h5, self.snp_ids_h5, self.snp_annotations_h5) = read_genotypes_vcf_h5(self.vcf_file.name)
        (self.genotypes, self.unphased_genotypes, self.snp_ids, self.snp_annotations) = read_genotypes_vcf(self.vcf_file.name)
        self.unphased_genotypes_h5 = sorted((i for i in self.unphased_genotypes_h5))
        self.snp_ids_h5 = sorted(self.snp_ids_h5)
        self.unphased_genotypes.sort()
        self.snp_ids.sort()

    def test_SNPPosAnnotations(self):
        for i in range(len(self.expected_pos_annotations)):
            print self.expected_pos_annotations[i], self.snp_annotations['pos'][i], self.snp_annotations_h5['pos'][i]
            assert self.expected_pos_annotations[i] == self.snp_annotations['pos'][i] == self.snp_annotations_h5['pos'][i]

    def test_SNPIds(self):
        print self.expected_snp_ids
        print self.snp_ids
        print self.snp_ids_h5
        for i in range(len(self.expected_pos_annotations)):
            print self.expected_snp_ids[i], self.snp_ids[i], self.snp_ids_h5[i]
            assert self.expected_snp_ids[i] == self.snp_ids[i] == self.snp_ids_h5[i]

    def test_GenotypesFirstIndividual(self):
        """checks the genotypes of the first individual (the first row)"""
#        print ((int(x) for x in self.genotypes[0][4:]), self.genotypes_h5[0,:])
#        print ([int(x) for x in self.genotypes[0][4:]] == self.genotypes_h5[0,:])
#        print numpy.alltrue([int(x) for x in self.genotypes[0][4:]] == self.genotypes_h5[0,:])
        assert numpy.alltrue([int(x) for x in self.genotypes[0][4:]] == self.genotypes_h5[0,:])

class TestSimpleVCF2(TestSimpleVCF):
    """
    Another simple VCF file
    """
    sample_vcf = r'''#
#CHROM  POS     ID      REF     ALT     QUAL    FILTER  INFO    FORMAT  HG00096 HG00097 HG00099 HG00100 HG00101
14      23033832        rs186383615     T       C       100     PASS    LDAF=0.0016;THETA=0.0004;AA=T;AN=2184;VT=SNP;SNPSOURCE=LOWCOV;ERATE=0.0003;RSQ=0.8538;AVGPOST=0.9995;AC=3;AF=0.0014;AFR_AF=0.0020;EUR_AF=0.0026 GT:DS:GL        1|0:0.000:-0.01,-1.48,-5.00     1|0:0.000:0.00,-5.00,-5.00      0|0:0.000:-0.00,-3.36,-5.00     1|1:0.000:-0.00,-3.19,-5.00     0|0:0.000:-0.00,-4.22,-5.00
14      23033840        rs1051189       G       A       100     PASS    RSQ=0.9958;AC=248;THETA=0.0004;AA=G;AN=2184;AVGPOST=0.9990;VT=SNP;LDAF=0.1138;SNPSOURCE=LOWCOV;ERATE=0.0003;AF=0.11;ASN_AF=0.15;AMR_AF=0.07;AFR_AF=0.13;EUR_AF=0.10     GT:DS:GL        0|0:0.000:-0.01,-1.77,-5.00     0|0:0.000:0.00,-5.00,-5.00      1|1:0.000:-0.00,-2.31,-5.00     0|0:0.000:-0.00,-3.19,-5.00     1|0:0.000:-0.00,-2.31,-5.00
14      23033854        rs1051190       C       G       100     PASS    RSQ=0.9958;AC=248;THETA=0.0004;AA=G;AN=2184;AVGPOST=0.9990;VT=SNP;LDAF=0.1138;SNPSOURCE=LOWCOV;ERATE=0.0003;AF=0.11;ASN_AF=0.15;AMR_AF=0.07;AFR_AF=0.13;EUR_AF=0.10     GT:DS:GL        1|0:0.000:-0.01,-1.77,-5.00     1|1:0.000:0.00,-5.00,-5.00      0|0:0.000:-0.00,-2.31,-5.00     0|1:0.000:-0.00,-3.19,-5.00     1|1:0.000:-0.00,-2.31,-5.00
14      23033888        rs1051191       G       A       100     PASS    RSQ=0.9958;AC=248;THETA=0.0004;AA=G;AN=2184;AVGPOST=0.9990;VT=SNP;LDAF=0.1138;SNPSOURCE=LOWCOV;ERATE=0.0003;AF=0.11;ASN_AF=0.15;AMR_AF=0.07;AFR_AF=0.13;EUR_AF=0.10     GT:DS:GL        0|0:0.000:-0.01,-1.77,-5.00     1|0:0.000:0.00,-5.00,-5.00      0|0:0.000:-0.00,-2.31,-5.00     1|0:0.000:-0.00,-3.19,-5.00     1|0:0.000:-0.00,-2.31,-5.00
'''
    expected_pos_annotations = "23033832 23033840 23033854 23033888".split()
    expected_snp_ids = sorted("rs186383615 rs1051189 rs1051190 rs1051191".split())

class TestUnphasedVCF2(TestSimpleVCF):
    """
    A file containing unphased data. Unphased individuals are not implemented yet, but the function should work without errors anyway.
    """
    sample_vcf = r'''#
#CHROM  POS     ID      REF     ALT     QUAL    FILTER  INFO    FORMAT  HG00096 HG00097 HG00099 HG00100 HG00101
14      23033832        rs186383615     T       C       100     PASS    LDAF=0.0016;THETA=0.0004;AA=T;AN=2184;VT=SNP;SNPSOURCE=LOWCOV;ERATE=0.0003;RSQ=0.8538;AVGPOST=0.9995;AC=3;AF=0.0014;AFR_AF=0.0020;EUR_AF=0.0026 GT:DS:GL        1|0:0.000:-0.01,-1.48,-5.00     1/0:0.000:0.00,-5.00,-5.00      0/0:0.000:-0.00,-3.36,-5.00     1|1:0.000:-0.00,-3.19,-5.00     0|0:0.000:-0.00,-4.22,-5.00
14      23033840        rs1051189       G       A       100     PASS    RSQ=0.9958;AC=248;THETA=0.0004;AA=G;AN=2184;AVGPOST=0.9990;VT=SNP;LDAF=0.1138;SNPSOURCE=LOWCOV;ERATE=0.0003;AF=0.11;ASN_AF=0.15;AMR_AF=0.07;AFR_AF=0.13;EUR_AF=0.10     GT:DS:GL        0|0:0.000:-0.01,-1.77,-5.00     0/0:0.000:0.00,-5.00,-5.00      1|1:0.000:-0.00,-2.31,-5.00     0|0:0.000:-0.00,-3.19,-5.00     1|0:0.000:-0.00,-2.31,-5.00
14      23033854        rs1051190       C       G       100     PASS    RSQ=0.9958;AC=248;THETA=0.0004;AA=G;AN=2184;AVGPOST=0.9990;VT=SNP;LDAF=0.1138;SNPSOURCE=LOWCOV;ERATE=0.0003;AF=0.11;ASN_AF=0.15;AMR_AF=0.07;AFR_AF=0.13;EUR_AF=0.10     GT:DS:GL        1|0:0.000:-0.01,-1.77,-5.00     1|1:0.000:0.00,-5.00,-5.00      0|0:0.000:-0.00,-2.31,-5.00     0|1:0.000:-0.00,-3.19,-5.00     1|1:0.000:-0.00,-2.31,-5.00
14      23033888        rs1051191       G       A       100     PASS    RSQ=0.9958;AC=248;THETA=0.0004;AA=G;AN=2184;AVGPOST=0.9990;VT=SNP;LDAF=0.1138;SNPSOURCE=LOWCOV;ERATE=0.0003;AF=0.11;ASN_AF=0.15;AMR_AF=0.07;AFR_AF=0.13;EUR_AF=0.10     GT:DS:GL        0|0:0.000:-0.01,-1.77,-5.00     1|0:0.000:0.00,-5.00,-5.00      0/0:0.000:-0.00,-2.31,-5.00     1|0:0.000:-0.00,-3.19,-5.00     1|0:0.000:-0.00,-2.31,-5.00
'''
    expected_pos_annotations = "23033832 23033840 23033854 23033888".split()
    expected_snp_ids = sorted("rs186383615 rs1051189 rs1051190 rs1051191".split())

class TestLessAnnotations(TestSimpleVCF):
    """
    A VCF file containing less annotations (let's see what happens).
    """
    sample_vcf = r'''#
#CHROM  POS     ID      REF     ALT     QUAL    FILTER  INFO    FORMAT  HG00096 HG00097 HG00099 HG00100 HG00101
14      23033832        rs186383615     T       C       100     PASS    LDAF=0.0016;THETA=0.0004;AA=T;AN=2184;VT=SNP;SNPSOURCE=LOWCOV;ERATE=0.0003;RSQ=0.8538;AVGPOST=0.9995;AC=3;AF=0.0014;AFR_AF=0.0020;EUR_AF=0.0026 GT:DS:GL        1|0     1|0     0|0     1|1     0|0
14      23033840        rs1051189       G       A       100     PASS    RSQ=0.9958;AC=248;THETA=0.0004;AA=G;AN=2184;AVGPOST=0.9990;VT=SNP;LDAF=0.1138;SNPSOURCE=LOWCOV;ERATE=0.0003;AF=0.11;ASN_AF=0.15;AMR_AF=0.07;AFR_AF=0.13;EUR_AF=0.10     GT:DS:GL        0|0     0|0     1|1     0|0     1|0
14      23033854        rs1051190       C       G       100     PASS    RSQ=0.9958;AC=248;THETA=0.0004;AA=G;AN=2184;AVGPOST=0.9990;VT=SNP;LDAF=0.1138;SNPSOURCE=LOWCOV;ERATE=0.0003;AF=0.11;ASN_AF=0.15;AMR_AF=0.07;AFR_AF=0.13;EUR_AF=0.10     GT:DS:GL        1|0     1|1     0|0     0|1     1|1
14      23033888        rs1051191       G       A       100     PASS    RSQ=0.9958;AC=248;THETA=0.0004;AA=G;AN=2184;AVGPOST=0.9990;VT=SNP;LDAF=0.1138;SNPSOURCE=LOWCOV;ERATE=0.0003;AF=0.11;ASN_AF=0.15;AMR_AF=0.07;AFR_AF=0.13;EUR_AF=0.10     GT:DS:GL        0|0     1|0     0|0     1|0     1|0
'''
    expected_pos_annotations = "23033832 23033840 23033854 23033888".split()
    expected_snp_ids = sorted("rs186383615 rs1051189 rs1051190 rs1051191".split())


def test_VCF2BinaryHDF5():
    """
    >>> from tempfile import NamedTemporaryFile
    >>> vcf_file = NamedTemporaryFile(delete=False)
    >>> sample_vcf = r'''#
    ... #CHROM  POS     ID      REF     ALT     QUAL    FILTER  INFO    FORMAT  HG00096 HG00097 HG00099 HG00100 HG00101
    ... 14      23033832        rs186383615     T       C       100     PASS    LDAF=0.0016;THETA=0.0004;AA=T;AN=2184;VT=SNP;SNPSOURCE=LOWCOV;ERATE=0.0003;RSQ=0.8538;AVGPOST=0.9995;AC=3;AF=0.0014;AFR_AF=0.0020;EUR_AF=0.0026 GT:DS:GL        1|0:0.000:-0.01,-1.48,-5.00     0|0:0.000:0.00,-5.00,-5.00      0|0:0.000:-0.00,-3.36,-5.00     0|1:0.000:-0.00,-3.19,-5.00     0|0:0.000:-0.00,-4.22,-5.00
    ... 14      23033840        rs1051189       G       A       100     PASS    RSQ=0.9958;AC=248;THETA=0.0004;AA=G;AN=2184;AVGPOST=0.9990;VT=SNP;LDAF=0.1138;SNPSOURCE=LOWCOV;ERATE=0.0003;AF=0.11;ASN_AF=0.15;AMR_AF=0.07;AFR_AF=0.13;EUR_AF=0.10     GT:DS:GL        0|0:0.000:-0.01,-1.77,-5.00     0|0:0.000:0.00,-5.00,-5.00      0|1:0.000:-0.00,-2.31,-5.00     0|0:0.000:-0.00,-3.19,-5.00     1|0:0.000:-0.00,-2.31,-5.00
    ... 14      23033854        rs1051190       C       G       100     PASS    RSQ=0.9958;AC=248;THETA=0.0004;AA=G;AN=2184;AVGPOST=0.9990;VT=SNP;LDAF=0.1138;SNPSOURCE=LOWCOV;ERATE=0.0003;AF=0.11;ASN_AF=0.15;AMR_AF=0.07;AFR_AF=0.13;EUR_AF=0.10     GT:DS:GL        0|0:0.000:-0.01,-1.77,-5.00     1|0:0.000:0.00,-5.00,-5.00      0|0:0.000:-0.00,-2.31,-5.00     0|1:0.000:-0.00,-3.19,-5.00     1|1:0.000:-0.00,-2.31,-5.00
    ... 14      23033888        rs1051191       G       A       100     PASS    RSQ=0.9958;AC=248;THETA=0.0004;AA=G;AN=2184;AVGPOST=0.9990;VT=SNP;LDAF=0.1138;SNPSOURCE=LOWCOV;ERATE=0.0003;AF=0.11;ASN_AF=0.15;AMR_AF=0.07;AFR_AF=0.13;EUR_AF=0.10     GT:DS:GL        0|0:0.000:-0.01,-1.77,-5.00     1|0:0.000:0.00,-5.00,-5.00      0|0:0.000:-0.00,-2.31,-5.00     1|0:0.000:-0.00,-3.19,-5.00     1|0:0.000:-0.00,-2.31,-5.00
    ... '''
    >>> vcf_file.write(sample_vcf)
    >>> vcf_file.close()
    >>> (indv_annotations, genotypes, unphased_genotypes, snp_ids, snp_annotations) = read_genotypes_vcf_h5(vcf_file.name)
    >>> print ' '.join(snp_annotations['pos'])
    23033832 23033840 23033854 23033888

    >>> for ind_id in range(len(indv_annotations)): #doctest: +ELLIPSIS
    ...     print indv_annotations[ind_id, 0], indv_annotations[ind_id, 1], indv_annotations[ind_id, 2], indv_annotations[ind_id, 3], indv_annotations[ind_id, 4],
    ...     for geno_value in genotypes[ind_id, :]:
    ...         print geno_value,
    ...     print 
    tmp... HG00096_1 nopop nocontinent X 1 0 0 0
    tmp... HG00096_2 nopop nocontinent X 0 0 0 0
    tmp... HG00097_1 nopop nocontinent X 0 0 1 1
    tmp... HG00097_2 nopop nocontinent X 0 0 0 0
    tmp... HG00099_1 nopop nocontinent X 0 0 0 0
    tmp... HG00099_2 nopop nocontinent X 0 1 0 0
    tmp... HG00100_1 nopop nocontinent X 0 0 0 1
    tmp... HG00100_2 nopop nocontinent X 1 0 1 0
    tmp... HG00101_1 nopop nocontinent X 0 1 1 1
    tmp... HG00101_2 nopop nocontinent X 0 0 1 0

    """

def test_VCF2Binary_noHDF5():
    """
    >>> from tempfile import NamedTemporaryFile
    >>> vcf_file = NamedTemporaryFile(delete=False)
    >>> sample_vcf = r'''#
    ... #CHROM  POS     ID      REF     ALT     QUAL    FILTER  INFO    FORMAT  HG00096 HG00097 HG00099 HG00100 HG00101
    ... 14      23033832        rs186383615     T       C       100     PASS    LDAF=0.0016;THETA=0.0004;AA=T;AN=2184;VT=SNP;SNPSOURCE=LOWCOV;ERATE=0.0003;RSQ=0.8538;AVGPOST=0.9995;AC=3;AF=0.0014;AFR_AF=0.0020;EUR_AF=0.0026 GT:DS:GL        1|0:0.000:-0.01,-1.48,-5.00     0|0:0.000:0.00,-5.00,-5.00      0|0:0.000:-0.00,-3.36,-5.00     0|1:0.000:-0.00,-3.19,-5.00     0|0:0.000:-0.00,-4.22,-5.00
    ... 14      23033840        rs1051189       G       A       100     PASS    RSQ=0.9958;AC=248;THETA=0.0004;AA=G;AN=2184;AVGPOST=0.9990;VT=SNP;LDAF=0.1138;SNPSOURCE=LOWCOV;ERATE=0.0003;AF=0.11;ASN_AF=0.15;AMR_AF=0.07;AFR_AF=0.13;EUR_AF=0.10     GT:DS:GL        0|0:0.000:-0.01,-1.77,-5.00     0|0:0.000:0.00,-5.00,-5.00      0|1:0.000:-0.00,-2.31,-5.00     0|0:0.000:-0.00,-3.19,-5.00     1|0:0.000:-0.00,-2.31,-5.00
    ... 14      23033854        rs1051190       C       G       100     PASS    RSQ=0.9958;AC=248;THETA=0.0004;AA=G;AN=2184;AVGPOST=0.9990;VT=SNP;LDAF=0.1138;SNPSOURCE=LOWCOV;ERATE=0.0003;AF=0.11;ASN_AF=0.15;AMR_AF=0.07;AFR_AF=0.13;EUR_AF=0.10     GT:DS:GL        0|0:0.000:-0.01,-1.77,-5.00     1|0:0.000:0.00,-5.00,-5.00      0|0:0.000:-0.00,-2.31,-5.00     0|1:0.000:-0.00,-3.19,-5.00     1|1:0.000:-0.00,-2.31,-5.00
    ... 14      23033888        rs1051191       G       A       100     PASS    RSQ=0.9958;AC=248;THETA=0.0004;AA=G;AN=2184;AVGPOST=0.9990;VT=SNP;LDAF=0.1138;SNPSOURCE=LOWCOV;ERATE=0.0003;AF=0.11;ASN_AF=0.15;AMR_AF=0.07;AFR_AF=0.13;EUR_AF=0.10     GT:DS:GL        0|0:0.000:-0.01,-1.77,-5.00     1|0:0.000:0.00,-5.00,-5.00      0|0:0.000:-0.00,-2.31,-5.00     1|0:0.000:-0.00,-3.19,-5.00     1|0:0.000:-0.00,-2.31,-5.00
    ... '''
    >>> vcf_file.write(sample_vcf)
    >>> vcf_file.close()
    >>> (indv_annotations, genotypes, unphased_genotypes, snp_ids, snp_annotations) = read_genotypes_vcf_h5(vcf_file.name)
    >>> print ' '.join(snp_annotations['pos'])
    23033832 23033840 23033854 23033888

    >>> for ind_id in range(len(indv_annotations)): #doctest: +ELLIPSIS
    ...     print indv_annotations[ind_id, 0], indv_annotations[ind_id, 1], indv_annotations[ind_id, 2], indv_annotations[ind_id, 3], indv_annotations[ind_id, 4],
    ...     for geno_value in genotypes[ind_id, :]:
    ...         print geno_value,
    ...     print
    tmp... HG00096_1 nopop nocontinent X 1 0 0 0
    tmp... HG00096_2 nopop nocontinent X 0 0 0 0
    tmp... HG00097_1 nopop nocontinent X 0 0 1 1
    tmp... HG00097_2 nopop nocontinent X 0 0 0 0
    tmp... HG00099_1 nopop nocontinent X 0 0 0 0
    tmp... HG00099_2 nopop nocontinent X 0 1 0 0
    tmp... HG00100_1 nopop nocontinent X 0 0 0 1
    tmp... HG00100_2 nopop nocontinent X 1 0 1 0
    tmp... HG00101_1 nopop nocontinent X 0 1 1 1
    tmp... HG00101_2 nopop nocontinent X 0 0 1 0
    """


def test_parseIndividualsFile():
    """
    >>> individuals_dict = parse_individuals_file(
    ...     individuals_file_path="./data/individuals/individuals_annotations.txt")
    >>> print sorted([name for name in individuals_dict.keys()])[0:10]
    ['HG00096', 'HG00097', 'HG00099', 'HG00100', 'HG00101', 'HG00102', 'HG00103', 'HG00104', 'HG00106', 'HG00108']
	>>> print individuals_dict["HG01083"] == {'continent': 'AMR', 'subpop': 'PUR', 'phenotype1': 'good'}
	True
	>>> print individuals_dict['HG00113'] == {'continent': 'EUR', 'subpop': 'GBR', 'phenotype1': 'bad'}
	True
    """



def test_printBinary():
    """
    >>> from tempfile import NamedTemporaryFile
    >>> import optparse
    >>> options = optparse.OptionParser()
    >>> options.use_hdf5 = False
    >>> options.debug = False
    >>> options.individuals_file = "./data/individuals/individuals_annotations.txt"
    >>> vcf_file = NamedTemporaryFile(delete=False)
    >>> sample_vcf = r'''#
    ... #CHROM  POS     ID      REF     ALT     QUAL    FILTER  INFO    FORMAT  HG00096 HG00097 HG00099 HG00100 HG00101
    ... 14      23033832        rs186383615     T       C       100     PASS    LDAF=0.0016;THETA=0.0004;AA=T;AN=2184;VT=SNP;SNPSOURCE=LOWCOV;ERATE=0.0003;RSQ=0.8538;AVGPOST=0.9995;AC=3;AF=0.0014;AFR_AF=0.0020;EUR_AF=0.0026 GT:DS:GL        1|0:0.000:-0.01,-1.48,-5.00     0|0:0.000:0.00,-5.00,-5.00      0|0:0.000:-0.00,-3.36,-5.00     0|1:0.000:-0.00,-3.19,-5.00     0|0:0.000:-0.00,-4.22,-5.00
    ... 14      23033840        rs1051189       G       A       100     PASS    RSQ=0.9958;AC=248;THETA=0.0004;AA=G;AN=2184;AVGPOST=0.9990;VT=SNP;LDAF=0.1138;SNPSOURCE=LOWCOV;ERATE=0.0003;AF=0.11;ASN_AF=0.15;AMR_AF=0.07;AFR_AF=0.13;EUR_AF=0.10     GT:DS:GL        0|0:0.000:-0.01,-1.77,-5.00     0|0:0.000:0.00,-5.00,-5.00      0|1:0.000:-0.00,-2.31,-5.00     0|0:0.000:-0.00,-3.19,-5.00     1|0:0.000:-0.00,-2.31,-5.00
    ... 14      23033854        rs1051190       C       G       100     PASS    RSQ=0.9958;AC=248;THETA=0.0004;AA=G;AN=2184;AVGPOST=0.9990;VT=SNP;LDAF=0.1138;SNPSOURCE=LOWCOV;ERATE=0.0003;AF=0.11;ASN_AF=0.15;AMR_AF=0.07;AFR_AF=0.13;EUR_AF=0.10     GT:DS:GL        0|0:0.000:-0.01,-1.77,-5.00     1|0:0.000:0.00,-5.00,-5.00      0|0:0.000:-0.00,-2.31,-5.00     0|1:0.000:-0.00,-3.19,-5.00     1|1:0.000:-0.00,-2.31,-5.00
    ... 14      23033888        rs1051191       G       A       100     PASS    RSQ=0.9958;AC=248;THETA=0.0004;AA=G;AN=2184;AVGPOST=0.9990;VT=SNP;LDAF=0.1138;SNPSOURCE=LOWCOV;ERATE=0.0003;AF=0.11;ASN_AF=0.15;AMR_AF=0.07;AFR_AF=0.13;EUR_AF=0.10     GT:DS:GL        0|0:0.000:-0.01,-1.77,-5.00     1|0:0.000:0.00,-5.00,-5.00      0|0:0.000:-0.00,-2.31,-5.00     1|0:0.000:-0.00,-3.19,-5.00     1|0:0.000:-0.00,-2.31,-5.00
    ... '''
    >>> vcf_file.write(sample_vcf)
    >>> vcf_file.close()
    >>> print_binary_file(vcf_file.name, options) # doctest: +ELLIPSIS
    #gene chromosome_id snps
    #SNP IDS: rs186383615 rs1051189 rs1051190 rs1051191
    #Chromosome: 14 14 14 14
    #Position: 23033832 23033840 23033854 23033888
    #Ref. allele: T G C G
    tmp... HG00096_1 GBR EUR X 1 0 0 0
    tmp... HG00097_1 GBR EUR X 0 0 1 1
    tmp... HG00099_1 GBR EUR X 0 0 0 0
    tmp... HG00100_1 GBR EUR X 0 0 0 1
    tmp... HG00101_1 GBR EUR X 0 1 1 1
    tmp... HG00096_2 GBR EUR X 0 0 0 0
    tmp... HG00097_2 GBR EUR X 0 0 0 0
    tmp... HG00099_2 GBR EUR X 0 1 0 0
    tmp... HG00100_2 GBR EUR X 1 0 1 0
    tmp... HG00101_2 GBR EUR X 0 0 1 0


    This script can also use an internal HDF5 file to store genotypes. This 
    requires the h5py and HDF5 libraries to be installed, but is more memory
    efficient, as genotypes are stored on disk instead of RAM memory.
    When using this option, the output format is slighly different, as the order
    of individuals is more correct. However, the results are the same.
    >>> options.use_hdf5 = True
    >>> print_binary_file(vcf_file.name, options) # doctest: +ELLIPSIS
    #gene chromosome_id snps
    #SNP IDS: rs186383615 rs1051189 rs1051190 rs1051191
    #Chromosome: 14 14 14 14
    #Position: 23033832 23033840 23033854 23033888
    #Ref. allele: T G C G
    tmp... HG00096_1 GBR EUR X 1 0 0 0
    tmp... HG00096_2 GBR EUR X 0 0 0 0
    tmp... HG00097_1 GBR EUR X 0 0 1 1
    tmp... HG00097_2 GBR EUR X 0 0 0 0
    tmp... HG00099_1 GBR EUR X 0 0 0 0
    tmp... HG00099_2 GBR EUR X 0 1 0 0
    tmp... HG00100_1 GBR EUR X 0 0 0 1
    tmp... HG00100_2 GBR EUR X 1 0 1 0
    tmp... HG00101_1 GBR EUR X 0 1 1 1
    tmp... HG00101_2 GBR EUR X 0 0 1 0

    >>> vcf_file.unlink(vcf_file.name)

    """
