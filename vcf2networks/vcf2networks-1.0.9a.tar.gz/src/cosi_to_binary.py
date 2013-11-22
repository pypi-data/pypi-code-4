#!/usr/bin/env python
"""
Convert a COSI .hap output to a binary file


Example .binary file:

    ALG10 HG00096_1 GBR EUR X 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
    ALG10 HG00097_1 GBR EUR X 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
    ALG10 HG00099_1 GBR EUR X 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 1 0
    ALG10 HG00100_1 GBR EUR X 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
    ALG10 HG00101_1 GBR EUR X 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 1 0 1 1 1 0 0 0 0 0 0 1 0 0 0
    ALG10 HG00102_1 GBR EUR X 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
    ALG10 HG00103_1 GBR EUR X 1 1 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 1 0
    ALG10 HG00104_1 GBR EUR X 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 1 0 1 0 0 0 0 0 0 0 0 0 0 0 0
    ALG10 HG00106_1 GBR EUR X 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
    ALG10 HG00108_1 GBR EUR X 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0
    ALG10 HG00109_1 GBR EUR X 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0

"""
import optparse
import logging
import os
import numpy
import gzip

def get_options():
    parser = optparse.OptionParser(usage="python %prog -f hapfile", description=__doc__)
    parser.add_option('-f', '--hapfile', dest='hapfile', 
            help='Cosi .hap file', default=False)
    parser.add_option('-u', '--no-debug', dest='debug', action='store_false', default=True)
    parser.add_option('-m', '--maf', '--maf-filter', dest='maf_filter', type='float',
            help='Maf Filter. Must be a float number, from 0 to 1. Default: %default',
            default=0.01)
    (options, args) = parser.parse_args()
    
    if options.debug is True:
        logging.basicConfig(level=logging.DEBUG, filename='logs/cosi_to_binary.log')

    if (options.hapfile is False) and (len(args) == 0):
        parser.print_help()
        parser.error('cosi_to_binary.py error: no cosi hap file provided')

    try:
        hapfile_path = ''
        if options.hapfile is not False:
            hapfile_path = options.hapfile
        elif args != '':
            hapfile_path = args[0]
        if os.stat(hapfile_path).st_size == 0:
            parser.error("file {0} is empty".format(hapfile_path))
    except:
        print __doc__
        parser.error("Can not open cosi hap file {0}".format(options.hapfile))


    return (hapfile_path, options.maf_filter)



def read_pos_file(posfile_path, maf_filter=0.01):
    """
    Read a COSI pos file and get a list of all the SNPs that pass a MAF filter.

    NOTE: this function is implemented, but not used in the analysis, as I prefer to make the MAF filtering step when reading the hap file.


    Example pos_file:

    >>> from tempfile import NamedTemporaryFile
    >>> posfile = NamedTemporaryFile(delete=False)
    >>> posfile.write(r'''
    ... SNP     CHROM   CHROM_POS       ALLELE1 FREQ1   ALLELE2 FREQ2
    ... 1       1       36      1       0.0000  2       1.0000
    ... 2       1       304     1       0.5000  2       0.5000
    ... 3       1       323     1       0.0001  2       0.9999
    ... 4       1       471     1       0.0000  2       1.0000
    ... 5       1       561     1       0.0000  2       1.0000
    ... 6       1       683     1       0.6000  2       0.4000
    ... 7       1       856     1       0.0000  2       1.0000
    ... 8       1       972     1       0.0167  2       0.9833
    ... 9       1       1312    1       1.0000  2       0.0000
    ... ''')
    >>> posfile.close()


    After filtering, SNPs 1, 3, 4, 5, 7 and 9 will be filtered out, because they don't pass the MAF filter test.
    >>> filtered_snps = read_pos_file(posfile.name)
    >>> print filtered_snps
    ['2', '6', '8']

    >>> posfile.unlink(posfile.name)
    """
    snps = []
    with open(posfile_path, 'r') as posfile_h:
        for line in posfile_h:
            if not line.strip() == '':
                if not line[0] in ('S', '#'):
                    fields = line.split()
                    snp_id = fields[0]
                    freq1 = float(fields[4])
                    if (freq1 < maf_filter) or (1-freq1 < maf_filter):
#                        print "filtered out", snp_id, freq1
                        pass
                    else:
                        snps.append(snp_id)
    return snps

sim_pops_dict = {'1': 'EUR', 
        '2': 'ASN',
        '3': 'AFR'
        }

def read_hap_file(cosifile_path, maf_filter=0.01):
    """
    Read a cosi .HAP file, containing the haplotypes of the individuals.

    maf_filter is a minor allele frequency filter. All the SNPs that have a maf lower than it, will be removed.

    =======================
    Example Input .hap File
    =======================

    Explanation of input cosi .hap file format: 

     * first column is the individual id
     * second column is the population ID
     * other columns are genotypes, one column per SNP.

    Each line is a different chromosome, one of the two haplotypes of each individual.

    Note that in this example, the first two columns are monomorphic (they are all 2s or 1s) and according to the MAF filter they will be removed.

    >>> from tempfile import NamedTemporaryFile
    >>> hapfile = NamedTemporaryFile(prefix='hap1', delete=False)
    >>> hapfile.write(r'''0       1       2 1 2 2 2 
    ... 1       1       2 1 2 2 2
    ... 2       1       2 1 2 2 1
    ... 3       1       2 1 2 2 2
    ... 4       1       2 1 1 1 1
    ... 5       1       2 1 1 2 2
    ... ''')
    >>> hapfile.close()

    ===========================
    Example Output binary file
    ===========================

    Explanation of output .binary file format: 

     * first column is a label to indicate that these are neutral simulations
     * second column is an id for population of the individual.
     * other columns are binary genotypes, one column per SNP.

    Each line is a different chromosome. The individuals id don't really matter, as these are fake individuals generated by the simulations.

    >>> print (read_hap_file(hapfile.name))  #doctest: +NORMALIZE_WHITESPACE
    #binary file v2. Simulations results. MAF filter: 0.01. Only SNPs that have MAF > 0.01 in each population are kept.
    #number of SNPs: 5. SNPs filtered: 2
    neutral_sim hap0_pop1 pop1 EUR X 1 1 1
    neutral_sim hap1_pop1 pop1 EUR X 1 1 1
    neutral_sim hap2_pop1 pop1 EUR X 1 1 0
    neutral_sim hap3_pop1 pop1 EUR X 1 1 1
    neutral_sim hap4_pop1 pop1 EUR X 0 0 0
    neutral_sim hap5_pop1 pop1 EUR X 0 1 1
    <BLANKLINE>

    >>> hapfile.unlink(hapfile.name)
    """
#    if pop_label is None:
#        pop_label = cosifile_path.split('.')[-1][-1]
    print "#binary file v2. Simulations results. MAF filter: {0}. Only SNPs that have MAF > {0} in each population are kept.".format(maf_filter)
    outputtemplate = "neutral_sim\tpop{0}\t{1}\n"
    output = ''
    if cosifile_path.split('.')[-1] == 'gz':
        cosifile = gzip.open(cosifile_path)
    else:
        cosifile = open(cosifile_path, 'r')

    firstline = ""
    while firstline is "":
        firstline = cosifile.readline().strip()
##            print firstline
    fields = firstline.split()
    first_haplotype = [int(g)-1 for g in fields[2:]]
    first_haplotype_pop = fields[1]
    n_snps = len(first_haplotype)
#   print n_snps
    cosifile.seek(0)

    all_haplotypes_bypop = {}
    # The first line is first added and then removed... not very nice, but effective.
    all_haplotypes_bypop['1'] = numpy.matrix(first_haplotype)
    all_haplotypes_bypop['2'] = numpy.matrix(first_haplotype)
    all_haplotypes_bypop['3'] = numpy.matrix(first_haplotype)
    for line in cosifile:
        logging.debug( len(line))
        logging.debug( line)
        if len(line)>1:
            fields = line.split()
#        ind_id = fields[0]
            pop_id = fields[1]
            pop = sim_pops_dict[pop_id]
            current_haplotype = [int(g)-1 for g in fields[2:]]
            # Append current chromosome to matrix. 
            # TODO: see if there is a better way to append a list to a matrix, in place
            all_haplotypes_bypop[pop_id] = numpy.vstack((all_haplotypes_bypop[pop_id], current_haplotype))
    all_haplotypes_bypop['1'] = numpy.delete(all_haplotypes_bypop['1'], (0), axis=0)
    all_haplotypes_bypop['2'] = numpy.delete(all_haplotypes_bypop['2'], (0), axis=0)
    all_haplotypes_bypop['3'] = numpy.delete(all_haplotypes_bypop['3'], (0), axis=0)
    logging.debug(all_haplotypes_bypop)
#    print all_haplotypes_bypop

    # Apply maf filter 
    filtered_columns = []       
    for (popid, all_haplotypes) in all_haplotypes_bypop.items():
#        print popid, len(all_haplotypes)
        if len(all_haplotypes) == 1:
            continue
        for position in xrange(n_snps):
            current_freq = numpy.average(all_haplotypes[:, position])
            if (1-current_freq < maf_filter) or (current_freq < maf_filter):
                filtered_columns.append(position)

#    print filtered_columns
    print "#number of SNPs: {0}. SNPs filtered: {1}".format(n_snps, len(set(filtered_columns)))
    for popid, all_haplotypes in all_haplotypes_bypop.items():
        indlabel = "hap{0}_pop" + popid
        poplabel = "pop" + popid
        contlabel = sim_pops_dict[popid]
        kept_columns = [n for n in xrange(n_snps) if n not in filtered_columns]
        all_haplotypes = all_haplotypes[:, kept_columns]
        all_haplotypes_list = all_haplotypes.tolist()
        for hap_id in range(len(all_haplotypes_list)):
            chromosome = all_haplotypes_list[hap_id]
            output += "neutral_sim " + indlabel.format(hap_id) + " " + poplabel + " " + contlabel + " X " + ' '.join(str(h) for h in chromosome) + "\n"
    return output

def main():
    (hapfile, maf_filter) = get_options()
    print read_hap_file(hapfile, maf_filter)

if __name__ == '__main__':
    main()


