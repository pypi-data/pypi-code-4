#!/usr/bin/env python
"""
Parse a .vcf format and produce genotypes to be added to a genotype network
"""
import logging
import optparse
import os
import gzip
import cPickle
import numpy
import tempfile
from custom_exceptions import *

class DataProcessingError(Exception):
    pass

def get_options():
    parser = optparse.OptionParser(usage="python {0} -f genotypes.vcf".format(__file__), description=__doc__)
    parser.add_option('-g', '-f', '--genotypes', dest='genotypes_file', 
            help='File containing the genotypes in vcf format', default=False)
    parser.add_option('-i', '--individuals', dest='individuals_file', 
            help='File containing the list of individuals and populations', default="data/individuals/individuals_annotations.txt")
    parser.add_option('-d', '--hdf5', '--h5',
            help='Use HDF5 internal storage. More memory efficient, but requires the h5py library to be installed.',
            dest='use_hdf5', action='store_true', default=False)
    parser.add_option('-u', '--debug', dest='debug', action='store_true', default=True)
    (options, args) = parser.parse_args()
    
    if options.debug is True:
        logging.basicConfig(level=logging.DEBUG, filename='logs/vcf_to_binary_convert.log')

    if (options.genotypes_file is False) and (len(args) == 0):
        parser.print_help()
        parser.error('parse_genotypes.py error: no genotypes file provided')
    try:
        genotypes_file_path = ''
        if options.genotypes_file is not False:
            genotypes_file_path = options.genotypes_file
        elif args != '':
            genotypes_file_path = args[0]
        if os.stat(genotypes_file_path).st_size == 0:
            parser.error("file {0} is empty".format(genotypes_file_path))
    except:
        print __doc__
        parser.error("Can not open genotypes file {0}".format(options.genotypes_file))

    return (genotypes_file_path, options)

def read_genotypes_vcf_h5(vcf_file_path, individuals_dict=False, gene_name=False):
    """
    Parse genotypes file in vcf format. Store intermediate variables into an HDF5 file, saving memory.

    Example vcf format:

    ::

        14      23033832        rs186383615     T       C       100     PASS    LDAF=0.0016;THETA=0.0004;AA=T;AN=2184;VT=SNP;SNPSOURCE=LOWCOV;ERATE=0.0003;RSQ=0.8538;AVGPOST=0.9995;AC=3;AF=0.0014;AFR_AF=0.0020;EUR_AF=0.0026 GT:DS:GL        0|0:0.000:-0.01,-1.48,-5.00     0|0:0.000:0.00,-5.00,-5.00      0|0:0.000:-0.00,-3.36,-5.00     0|0:0.000:-0.00,-3.19,-5.00     0|0:0.000:-0.00,-4.22,-5.00
        14      23033838        rs1051189       G       A       100     PASS    RSQ=0.9958;AC=248;THETA=0.0004;AA=G;AN=2184;AVGPOST=0.9990;VT=SNP;LDAF=0.1138;SNPSOURCE=LOWCOV;ERATE=0.0003;AF=0.11;ASN_AF=0.15;AMR_AF=0.07;AFR_AF=0.13;EUR_AF=0.10     GT:DS:GL        0|0:0.000:-0.01,-1.77,-5.00     0|0:0.000:0.00,-5.00,-5.00      0|0:0.000:-0.00,-2.31,-5.00     0|0:0.000:-0.00,-3.19,-5.00     
    
    How to parse the vcf format:

    * genotypes are in the column after the 10th, one column per individual
    * 0|0 means that the individual is homozygote for the reference allele. The rest of the genotype line are quality scores etc..
    * 0/0 means that the genotype is unphased, so it should be discarded
    * as another example, 0|1 means that the first chromosome has the ref allele, and the second has the alternative allele.
    

    ===================
    Example and doctest
    ===================


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

    >>> for ind_id in range(len(indv_annotations)): 
    ...     print indv_annotations[ind_id, 0], indv_annotations[ind_id, 1], indv_annotations[ind_id, 2], indv_annotations[ind_id, 3], indv_annotations[ind_id, 4],
    ...     for geno_value in genotypes[ind_id, :]:
    ...         print geno_value,
    ...     print #doctest: +ELLIPSIS
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
    logging.debug( "parsing " + vcf_file_path)
    import h5py

    if vcf_file_path[-3:] == '.gz':
        vcf_file = gzip.open(vcf_file_path)
    else: 
        vcf_file = open(vcf_file_path, 'r')
    
    if gene_name is False:
        h5_file = tempfile.NamedTemporaryFile()
        gene_name = h5_file.name.split('/')[-1]
    else:
        h5_file = open('./data/hdf5/' + gene_name + '_genotypes.hdf5', 'w')
    h5_tmp_file = h5py.File(h5_file.name, 'w')

    snp_ids = []
    snp_annotations = {"chrom": [], "pos": [], "ref":[]}
    snp_number = 0
    current_numbercolumns = 100
    for snp_line in vcf_file:
        if snp_line.strip() == '':
            continue

        # READ HEADERS - FIRST LINE
        if snp_line.startswith('#CHROM'):
            snp_fields = snp_line.split()
            snp_id = snp_fields[2]
            individuals_names = snp_fields[9:]

            n_individuals = len(individuals_names)
            my_dtypes = numpy.dtype('S10')#, 'S10', 'S10', 'S2')
            # genotype_line is a matrix containing one individual per row, and one genotype per column.
            genotype_line = h5_tmp_file.create_dataset("genotype_line", (n_individuals*2, current_numbercolumns), dtype='b', maxshape=(n_individuals*2, None))
            indv_annotations = h5_tmp_file.create_dataset("indv_annotations", (n_individuals*2, 5), dtype='|S15')
            indv_annotations[:, 0] = gene_name

            if individuals_dict is not False:
                # if the headers contain indv_annotations on individuals, use and include them in the output file.
                individuals_pops = [individuals_dict[name]['subpop'] for name in individuals_names]
                individuals_continents = [individuals_dict[name]['continent'] for name in individuals_names]

                indv_annotations[0::2, 1] = [name + '_1' for name in individuals_names]
                indv_annotations[1::2, 1] = [name + '_2' for name in individuals_names]

                indv_annotations[0::2, 2] = individuals_pops
                indv_annotations[1::2, 2] = individuals_pops

                indv_annotations[0::2, 3] = individuals_continents
                indv_annotations[1::2, 3] = individuals_continents

                indv_annotations[:, 4] = 'X'
            else:
                indv_annotations[0::2, 1] = [name + '_1' for name in individuals_names]
                indv_annotations[1::2, 1] = [name + '_2' for name in individuals_names]

                indv_annotations[:, 2] = "nopop"
                indv_annotations[:, 3] = "nocontinent"
                indv_annotations[:, 4] = "X"

#            unphased_genotypes      = [[name + '_unphased'] for name in individuals_names]
#            print indv_annotations[:,:]
            
        # READ DATA LINES
        if not snp_line.startswith('#'):
            print line
            snp_fields = snp_line.split(sep=None)
            (chromosome, position, snp_id, ref, alt, qual, filt, info, geno_format) = snp_fields[:9]
            snp_annotations["chrom"].append(snp_fields[0])
            snp_annotations["pos"].append(snp_fields[1])
            snp_annotations["ref"].append(snp_fields[3])

            snp_ids.append(snp_id)
            chromosome1          = [int(snp_fields[i][0]) for i in range(9, len(snp_fields))]
#            print len(chromosome1)
            chromosome2          = [int(snp_fields[i][2]) for i in range(9, len(snp_fields))]
            unphased_individuals = [snp_fields[i][1] for i in range(9, len(snp_fields))]
            if unphased_individuals.count('/') > 0:
                raise GenotypeNetworkInitError("unphased genotypes in {0}".format(snp_id))
#                logging.warn("unphased genotypes in {0}".format(snp_id))
            if chromosome1.count('2') > 0 or chromosome2.count('2') > 0:
                raise GenotypeNetworkInitError("triallelic SNP in {0}".format(snp_id))
                logging.warn("triallelic SNP in {0}".format(snp_id))

#            print chromosome1
            # TODO: filter out unphased individuals

            # Updating the number of columns in the genotype_line HDF5 array.
            if snp_number >= current_numbercolumns:
                current_numbercolumns += 100
                genotype_line.resize(size=current_numbercolumns, axis=1)
            genotype_line[::2,snp_number] = chromosome1
            genotype_line[1::2,snp_number] = chromosome2
            snp_number += 1

#            [unphased_genotypes[i].append(unphased_individuals[i]) for i in range(len(unphased_individuals))]
    genotype_line.resize(size=snp_number, axis=1) 

    snp_annotations_h5 = h5_tmp_file.create_dataset("snp_annotations", (snp_number, 4), "S15")
    snp_annotations_h5[:,0] = snp_ids
    snp_annotations_h5[:,1] = snp_annotations["chrom"]
    snp_annotations_h5[:,2] = snp_annotations["pos"]
    snp_annotations_h5[:,3] = snp_annotations["ref"]

    # TODO: filter out unphased individuals
#    genotype_lines = [genotype_line_1, genotype_line_2]
#    genotype_lines.extend(genotype_line_2)
    unphased_genotypes = []
    return((indv_annotations, genotype_line, unphased_genotypes, snp_ids, snp_annotations))


def read_genotypes_vcf(vcf_file_path, individuals_dict=False, individuals_file=""): # NOTE: the individuals_file here is passed only for improving the error message
    """
    Parse genotypes file in vcf format

    Example vcf format:

    ::

        14      23033832        rs186383615     T       C       100     PASS    LDAF=0.0016;THETA=0.0004;AA=T;AN=2184;VT=SNP;SNPSOURCE=LOWCOV;ERATE=0.0003;RSQ=0.8538;AVGPOST=0.9995;AC=3;AF=0.0014;AFR_AF=0.0020;EUR_AF=0.0026 GT:DS:GL        0|0:0.000:-0.01,-1.48,-5.00     0|0:0.000:0.00,-5.00,-5.00      0|0:0.000:-0.00,-3.36,-5.00     0|0:0.000:-0.00,-3.19,-5.00     0|0:0.000:-0.00,-4.22,-5.00
        14      23033838        rs1051189       G       A       100     PASS    RSQ=0.9958;AC=248;THETA=0.0004;AA=G;AN=2184;AVGPOST=0.9990;VT=SNP;LDAF=0.1138;SNPSOURCE=LOWCOV;ERATE=0.0003;AF=0.11;ASN_AF=0.15;AMR_AF=0.07;AFR_AF=0.13;EUR_AF=0.10     GT:DS:GL        0|0:0.000:-0.01,-1.77,-5.00     0|0:0.000:0.00,-5.00,-5.00      0|0:0.000:-0.00,-2.31,-5.00     0|0:0.000:-0.00,-3.19,-5.00     
    
    How to parse the vcf format:

    * genotypes are in the column after the 10th, one column per individual
    * 0|0 means that the individual is homozygote for the reference allele. The rest of the genotype line are quality scores etc..
    * 0/0 means that the genotype is unphased, so it should be discarded
    * as another example, 0|1 means that the first chromosome has the ref allele, and the second has the alternative allele.
    

    ===================
    Example and doctest
    ===================


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
    >>> (genotype_lines, unphased_genotypes, snp_ids, snp_annotations) = read_genotypes_vcf(vcf_file.name)
    >>> for genotype in genotype_lines: 
    ...     print(' '.join(genotype)) #doctest: +ELLIPSIS
    HG00096_1 nopop nocontinent X 1 0 0 0
    HG00097_1 nopop nocontinent X 0 0 1 1
    HG00099_1 nopop nocontinent X 0 0 0 0
    HG00100_1 nopop nocontinent X 0 0 0 1
    HG00101_1 nopop nocontinent X 0 1 1 1
    HG00096_2 nopop nocontinent X 0 0 0 0
    HG00097_2 nopop nocontinent X 0 0 0 0
    HG00099_2 nopop nocontinent X 0 1 0 0
    HG00100_2 nopop nocontinent X 1 0 1 0
    HG00101_2 nopop nocontinent X 0 0 1 0

    >>> print ' '.join(snp_annotations['pos'])
    23033832 23033840 23033854 23033888

    """
    logging.debug( vcf_file_path)

    if vcf_file_path[-3:] == '.gz':
        vcf_file = gzip.open(vcf_file_path)
    else: 
        vcf_file = open(vcf_file_path, 'r')

    snp_ids = []
    snp_annotations = {"chrom": [], "pos": [], "ref":[]}
#    print individuals_dict
    for snp_line in vcf_file:
#            logging.debug( ("snp line", snp_line[:20]))
        if snp_line.strip() == '':
            continue

        # READ HEADERS - FIRST LINE
        if snp_line.startswith('#CHROM'):
            snp_fields = snp_line.split()
#                individuals = individuals_names.fromkeys(snp_fields[9:], [])
            snp_id = snp_fields[2]
            individuals_names = snp_fields[9:]
            if individuals_dict is not False:
                for name in individuals_names:
                    if not individuals_dict.has_key(name):
                        raise InvalidIndividualsFile("The individual {0} is not defined in the individuals_file".format(name), individuals_file)
                individuals_pops = [individuals_dict[name]['subpop'] for name in individuals_names]
                individuals_continents = [individuals_dict[name]['continent'] for name in individuals_names]
                individuals_sex = ['X' for name in individuals_names]
                genotype_line_1 = [[name + '_1', individuals_dict[name]['subpop'], individuals_dict[name]['continent'], 'X']        for name in individuals_names]
                genotype_line_2 = [[name + '_2', individuals_dict[name]['subpop'], individuals_dict[name]['continent'], 'X']        for name in individuals_names]
            else:
                # This should be a fallback function in case the individuals_dict is missing, as in the simulations. #TODO: determine if this is really needed now.
                individuals_pops = ['no_pop' for name in individuals_names]
                individuals_continents = ['no_continent' for name in individuals_names]
                individuals_sex = ['X' for name in individuals_names]
                genotype_line_1 = [[name + '_1', 'nopop', 'nocontinent', 'X']        for name in individuals_names]
                genotype_line_2 = [[name + '_2', 'nopop', 'nocontinent', 'X']        for name in individuals_names]
#            genotype_line_1 = [[name + '_1']        for name in individuals_names]
#            genotype_line_2 = [[name + '_2']        for name in individuals_names]
#            unphased_genotypes      = [[name + '_unphased'] for name in individuals_names]
            
        # READ DATA LINES
        if not snp_line.startswith('#'):
            snp_fields = snp_line.split()
            if not len(snp_fields) > 8:
                raise DataProcessingError("""
                Wrong number of columns in the VCF file. 
                
                Check that:
                    - you are providing a correct VCF file with the -f (or -g) option, 
                    - there are no empty lines in the file
                    - all the comment lines begin with '#'
                    - each genotype line contains the same number of columns, at least 8

                Last line parsed: 
                 
            """ + snp_line)

            (chromosome, position, snp_id, ref, alt, qual, filt, info, geno_format) = snp_fields[:9]
            snp_annotations["chrom"].append(snp_fields[0])
            snp_annotations["pos"].append(snp_fields[1])
            snp_annotations["ref"].append(snp_fields[3])

            snp_ids.append(snp_id)
            chromosome1          = [snp_fields[i][0] for i in range(9, len(snp_fields))]
            chromosome2          = [snp_fields[i][2] for i in range(9, len(snp_fields))]
            unphased_individuals = [snp_fields[i][1] for i in range(9, len(snp_fields))]
            if unphased_individuals.count('/') > 0:
#                print snp_line
                raise GenotypeNetworkInitError("""
    The input file {0} contains an unphased Genotype.
    
    vcf2networks does not support unphased genotypes. 
    In vcf2networks, the two haplotypes of each individual are threated as separate entities; so, in case on unphased genotypes, there is no way to know to which haplotype a genotype would belong.
    You should filter your vcf file and remove all the unphased genotypes. For example:

        $: vcftools --phased --vcf {0} --recode --out {0}.filtered

        see http://vcftools.sourceforge.net for more options.

    The SNP containing the unphased genotype is: {1}. 

    Unphased genotypes can be distinguished from phased genotypes because the two genotypes are separated by a "/" instead of a "|".
    E.g.:
        0|0:0.000:-0.05,-0.94,-5.00 -> phased genotypes (0 and 0)
        0/0:0.000:-0.05,-0.94,-5.00 -> unphased genotypes (0 and 0)

    """.format(vcf_file.name, snp_id))


            if chromosome1.count('2') > 0 or chromosome2.count('2') > 0:
                raise GenotypeNetworkInitError("""
    The input file {0} contains a triallelic SNP.
    
    vcf2networks does not currently support triallelic SNPs, and does not support any other type of variation except for SNPs.
    You should filter your vcf file and remove all the genotypes which are not biallelic:
    
        $: vcftools --min-alleles 2 --max-alleles 2 --vcf {0} --recode --out {0}.filtered
        
        see http://vcftools.sourceforge.net for more options.

    The SNP containing the triallelic SNP is: {1}. 

    Triallelic genotypes can be distinguished because the "ALT" column contain more than one allele, and they contain a number different from 0 or 1 in their genotype columns:
    E.g.:
        2|0:0.000:-0.05,-0.94,-5.00 -> Triallelic SNP (the first chromosome has the allele "2")

        """.format(vcf_file.name, snp_id))

            # TODO: filter out unphased individuals
            
            [genotype_line_1[i].append(           chromosome1[i]) for i in range(len(chromosome1))]
            [genotype_line_2[i].append(           chromosome2[i]) for i in range(len(chromosome2))]
#            [     unphased_genotypes[i].append(  unphased_individuals[i]) for i in range(len(unphased_individuals))]

    # TODO: filter out unphased individuals
    genotype_lines = genotype_line_1
    genotype_lines.extend(genotype_line_2)
    unphased_genotypes = []
    return((genotype_lines, unphased_genotypes, snp_ids, snp_annotations))



def parse_individuals_file(individuals_file_path="./data/individuals/individuals_annotations.txt",
                                pickle_from_file_if_possible=False,
                                picklefile='./data/pickles/individuals_dict.pickle'):
    """
    Parse the file containing info on individuals and populations, 
    return a dictionary of individuals and annotations.

    ++++++++++++++++++++++++++++
    Example of individuals file:
    ++++++++++++++++++++++++++++

    #ID POP CONTINENT   PHENOTYPE1
    HG00096 GBR     EUR     happy
    HG00097 GBR     EUR     happy
    HG00099 GBR     EUR     sad
    HG00100 GBR     EUR     sad
    HG00101 GBR     EUR     happy
    HG00102 GBR     EUR     happy
    HG00103 GBR     EUR     sad
    HG00104 GBR     EUR     happy
    HG00106 GBR     EUR     happy
    HG00108 GBR     EUR     sad
    HG00109 GBR     EUR     happy
    HG00110 GBR     EUR     happy

    >>> individuals_dict = parse_individuals_file()
    >>> print individuals_dict["HG01083"] == {'continent': 'AMR', 'subpop': 'PUR', 'phenotype1': ['ILLUMINA']}
    True
    >>> print individuals_dict['HG00113'] == {'continent': 'EUR', 'subpop': 'GBR', 'phenotype1': ['ABI_SOLID', 'ILLUMINA']}
    True

    """
    try:
        assert pickle_from_file_if_possible  # if the option pickle_from_file_if_possible is false, this block will return an error
        individuals_dict = cPickle.load(open(picklefile, 'r'))
#        individuals_dict['HG00096']
    except:
        individuals_dict = {}
        with open(individuals_file_path, 'r') as individuals_file:
            header = individuals_file.readline()
            if not header.startswith('#'):
                raise InvalidIndividualsFile(
                        'The first line in the individuals file must begin with a "#", and contain the names of the columns encoded in the file',
                        individuals_file_path)
            header_fields = header.replace('#', '').split()
            number_columns = len(header_fields)
#            print header_fields
#            print len(header_fields) <3
            if number_columns < 3:
                raise InvalidIndividualsFile(
                        'The individuals file should contain at least three columns, separated by tabulations.',
                        individuals_file_path)
            if header_fields[0].lower() not in ("id", "name", "individual"):
                raise InvalidIndividualsFile(
                        'The first column of the individuals file should be named "ID", or "individual", or "name"',
                        individuals_file_path)
            if header_fields[1].lower() not in ("pop", "population", "subpop", "group"):
                raise InvalidIndividualsFile(
                        'The second column of the individuals file should be named "POP", and describe the population of the individuals.\n\tIn future releases, this column will not be mandatory, but in the current version your individuals_file must contain a column named "POP" in the second position.\n\tSorry for the inconvenience.',
                        individuals_file_path)
            if header_fields[2].lower() not in ("continent", "cont", "continental_group"):
                raise InvalidIndividualsFile(
                        'The third column of the individuals file should be named "CONTINENT", and describe the continental group to which the individuals belong.\n\tIn future releases, this column will not be mandatory, but in the current version your individuals_file must contain a column named "CONTINENT" in the third position.\n\tSorry for the inconvenience.',
                        individuals_file_path)


            # Parsing the other rows
            for line in individuals_file:
                if not line.strip() == '':
                    fields = line.split()
                    if len(fields) != number_columns:
                        raise InvalidIndividualsFile(
                                """
    One line in your individuals file contains a different number of columns than expected.
    The line is:
    
        {0}
        
    It should have exactly {1} columns, defined as {2}""".format(line, number_columns, ', '.join(header_fields)), individuals_file)
                    ind = fields[0]
                    subpop = fields[1]
                    continent = fields[2]
#                    techniques = [x.replace(',','') for x in fields[3:]]
                    individuals_dict[ind] = {'subpop': subpop, 'continent': continent} 
                    for phenotype_id in range(len(header_fields[3:])):
#                        print header_fields[phenotype_id+3], fields[phenotype_id+3]
                        individuals_dict[ind][header_fields[phenotype_id+3]] = fields[phenotype_id+3]

        if pickle_from_file_if_possible is True:
            cPickle.dump(individuals_dict, open(picklefile, 'w'))
    return individuals_dict


def print_binary_file(genotypes_file_path, options):
    """
    Print the output of binary file conversion to screen.

    >>> from tempfile import NamedTemporaryFile
    >>> import optparse
    >>> options = optparse.OptionParser()
    >>> options.use_hdf5 = False
    >>> options.debug = False
    >>> options.individuals_file = "data/individuals/individuals_annotations.txt"
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
    >>> print(print_binary_file(vcf_file.name, options)) # doctest: +ELLIPSIS
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
    gene_name = genotypes_file_path.split('/')[-1].split('.',1)[0]
#    print options.individuals_file
    individuals_dict = parse_individuals_file(options.individuals_file)
    if options.use_hdf5 is True:
        (indv_annotations, genotypes, unphased_genotypes, snp_ids, snp_annotations) = read_genotypes_vcf_h5(genotypes_file_path, individuals_dict, gene_name)
    else:   
        (genotypes, unphased_genotypes, snp_ids, snp_annotations) = read_genotypes_vcf(genotypes_file_path, individuals_dict, options.individuals_file)
    output = '#gene chromosome_id snps'
    output += '\n#SNP IDS: ' + ' '.join(snp_ids)
    output += '\n#Chromosome: ' + ' '.join(snp_annotations['chrom'])
    output += '\n#Position: ' + ' '.join(snp_annotations['pos'])
    output += '\n#Ref. allele: ' + ' '.join(snp_annotations['ref'])
    if options.use_hdf5 is True:
        for ind_id in range(len(indv_annotations)):
            output += indv_annotations[ind_id, 0], indv_annotations[ind_id, 1], indv_annotations[ind_id, 2], indv_annotations[ind_id, 3], indv_annotations[ind_id, 4] + ' '
            for geno_value in genotypes[ind_id, :]:
                output += geno_value + ''
            output += ''
    else:
        for genotype in genotypes:
            output += '\n' + gene_name + ' ' + ' '.join(genotype)
    return output

if __name__ == '__main__':
    (genotypes_file_path, options) = get_options()
    print_binary_file(genotypes_file_path, options)
    logging.debug("Finished parsing file {0}".format(genotypes_file_path))

