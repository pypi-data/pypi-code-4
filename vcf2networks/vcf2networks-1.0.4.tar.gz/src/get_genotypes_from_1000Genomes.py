#!/usr/bin/env python
"""
Get the genotypes of the genes listed in <gene_list> from 1000genomes.

Uses tabix to retrieve the vcf file.

Usage
=========

   $: python get_genotypes.py -l data/n-glycan.coords


Inputs
==========

the List of genes file must contain the coordinates of each gene in the analysis, in the following format:

::
    
    DOLK    N-glycan        substrates      chr9    131707808       131710012
    RPN1    N-glycan        ost_complex     chr3    128338812       128399918
    ALG8    N-glycan        precursor_biosynthesis  chr11   77811987        77850699
    ALG9    N-glycan        precursor_biosynthesis  chr11   111652918       111750181
    UAP1    N-glycan        substrates      chr1    162531295       162569633
    ST6GAL1 N-glycan        branching2      chr3    186648314       186796341
    ALG2    N-glycan        precursor_biosynthesis  chr9    101978706       101984246
    ALG3    N-glycan        precursor_biosynthesis  chr3    183960116       183967313
    ALG1    N-glycan        precursor_biosynthesis  chr16   5083702 5137380
    ALG6    N-glycan        precursor_biosynthesis  chr1    63833260        63904233
    GANAB   N-glycan        cnx_crt chr11   62392297        62414104

Note that SNPs in the 1000genomes project are encoded to hg19, so the coordinates must be all refSeq hg19. You can use the script get_gene_coords.py to retrieve the coordinates automatically.


"""
import optparse
import subprocess
import os
import glob


def get_options():
    parser = optparse.OptionParser(usage="python %prog -l genes_coords.txt", description=__doc__)
    parser.add_option('-g', '-c', '-f', '--coordinates_file', '--coordinates', '--genes', dest='genes', 
            help='File containing the coordinates of each gene. The first column must contain the gene name; \
                        the second and third columns may contain anything, usually a pathway and subpathway classification;\
                        the third, fourth, and fifth column must contain the chromosome, start and end positions.\
                        See the documentation in the code of this script for more help. Default: %default', default=False)
    parser.add_option('-o', '--outputpath', '--output_path', dest='outputpath', 
            help='Directory where the vcf files will be saved. It must be already existing, because the script won\'t create it automatically. Default: %default', 
            default="./data/vcf/")
    parser.add_option('-u', '--url', '--baseurl', dest='baseurl', 
            help='Base URL to the file containing the whole genome data. Use {0} to replace the chromosome number. Default: %default', 
            default = "ftp://ftp.1000genomes.ebi.ac.uk/vol1/ftp/phase1/analysis_results/integrated_call_sets/ALL.chr{0}.integrated_phase1_v3.20101123.snps_indels_svs.genotypes.vcf.gz")
    parser.add_option('-r', '--flank', dest='flank', 
            help='Include a flanking region of size n, upstream and downstream of the gene start and end. Default: %default', default=0)
    parser.add_option('-i', '--index', '--force-generate-index', dest='force_index', action='store_true',
            help='Force generation of tabix index file. Default: %default', default=False)
    parser.add_option('-d', '--download', '--force-download', dest='force_download', action='store_true',
            help='Force download of vcf files. Default: %default', default=False)
    parser.add_option('--get_individuals_index', dest='get_individuals', action='store_true',
            help='Force download of Individuals index. Default: %default', default=False)
    parser.add_option('-p', '--only-print', dest='onlyprint', action='store_true',
            help='Only print commands, without actually downloading. Default: %default', default=False)
    parser.add_option('--debug', dest='debug', action='store_true', default=True)
    (options, args) = parser.parse_args()
    
    if options.debug is True:
        logging.basicConfig(level=logging.DEBUG, filename='logs/get_genotypes.log')

    if (options.genes is False) and (len(args) == 0):
        parser.print_help()
        parser.error('get_genotypes.py: genes file not defined.')

    try:
        genes_path = ''
        if options.genes is not False:
            genes_path = options.genes
        elif args != '':
            genes_path = args[0]
        if os.stat(genes_path).st_size == 0:
            parser.error("file {0} is empty".format(genes_path))
    except:
        print __doc__
        parser.error("Can not open genes file")

    genes = read_genes_file(genes_path)
    logging.debug(genes[:2])

    return (genes, options)

def read_genes_file(genes_path):
    """
    DOLK    N-glycan        substrates      chr9    131707808       131710012
    RPN1    N-glycan        ost_complex     chr3    128338812       128399918
    ALG8    N-glycan        precursor_biosynthesis  chr11   77811987        77850699
    ALG9    N-glycan        precursor_biosynthesis  chr11   111652918       111750181
    UAP1    N-glycan        substrates      chr1    162531295       162569633
    ST6GAL1 N-glycan        branching2      chr3    186648314       186796341
    ALG2    N-glycan        precursor_biosynthesis  chr9    101978706       101984246
    ALG3    N-glycan        precursor_biosynthesis  chr3    183960116       183967313
    ALG1    N-glycan        precursor_biosynthesis  chr16   5083702 5137380
    ALG6    N-glycan        precursor_biosynthesis  chr1    63833260        63904233
    GANAB   N-glycan        cnx_crt chr11   62392297        62414104

    """
    genes = [line.split() for line in open(genes_path, 'r')]
    return genes


def get_genotypes(genes, baseurl, force_index=False, force_download=False, get_individuals=False, flank=0, outputpath='data/vcf/', print_only=False):
    """
    Call tabix on 1000genomes server to get coordinates.

    Note: the URL to 1000genomes may change over time. If something doesn't work, check it.
    """
##    tabix_1000genomes_url = "ftp://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20100804/ALL.2of4intersection.20100804.genotypes.vcf.gz"
##    tabix_1000genomes_url = "ftp://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20110521/ALL.chr{0}.phase1_release_v3.20101123.snps_indels_svs.genotypes.vcf.gz"
##                             ftp://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20110521 
#    tabix_1000genomes_url = "ftp://ftp.1000genomes.ebi.ac.uk/vol1/ftp/phase1/analysis_results/integrated_call_sets/ALL.chr{0}.integrated_phase1_v3.20101123.snps_indels_svs.genotypes.vcf.gz"
    if baseurl[0:3] not in ("ftp", "htt"):
        tabix_1000genomes_url = '../../' + baseurl
        tabix_indexfile_template = baseurl + '.tbi'
    else:
        tabix_1000genomes_url = baseurl
        tabix_indexfile_template = './data/tabix_indexes/' + baseurl.split('/')[-1] + '.tbi'
    individuals_file = "phase1_integrated_calls.20101123.ALL.panel"
#    ftp://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20110521/phase1_integrated_calls.20101123.ALL.panel
    individuals_url = tabix_1000genomes_url.rsplit('/', 1)[0] + '/' + individuals_file

    print flank
    flank = int(flank)


    # Get individuals' info
    if get_individuals is True:
        print "\nDownloading individual infos\n"
        print("wget {0}".format(individuals_url))
        subprocess.call("wget {0}".format(individuals_url).split())
        print("mv {0} data/individuals/{1}.individuals".format(individuals_file, individuals_file))
        subprocess.call("mv {0} data/individuals/{1}.individuals".format(individuals_file, individuals_file).split())

#    report_table_content = 'gene\tpathway\tsubpathway\tchromosome\tstart\tend\ttot_snps\tgene_length\tsnp_per_kb\n'
    report_table_content = 'gene\tpathway\tsubpathway\tchromosome\tstart\tend\tgene_length\n'
    for fields in genes:
        (gene,pathway,subpathway,chromosome,start,end) = fields[:6]
        start = int(start) - flank
        end   = int(end)   + flank
        
        chromosome = chromosome.replace('chr', '')
        print "\nDownloading genotypes for gene {0}, {1}:{2}-{3}".format(gene, chromosome, start,end)
        index_command = "../../bin/tabix -f -p vcf {0}".format(tabix_1000genomes_url.format(chromosome))
        command = "../../bin/tabix -p vcf -h {0} {1}:{2}-{3}".format(tabix_1000genomes_url.format(chromosome), chromosome, start, end)
        print (tabix_indexfile_template.format(chromosome))
        if force_index is True or not (os.path.exists(tabix_indexfile_template.format(chromosome))):
            print "- generating indexes", index_command
            if print_only is False:
                subprocess.call(index_command.split(), cwd='./data/tabix_indexes/')
        outputfilepath = outputpath + '/' + gene + '.vcf'
        gzoutputfilepath = outputfilepath + '.gz'

        if (os.path.isfile(gzoutputfilepath)) and (os.stat(gzoutputfilepath).st_size > 0) and (force_download is not True):
            print "- skipping download, as genotypes for gene {0} are already available in data/vcf/{1}.vcf. Use --force-download option to download again.".format(gene, gene)
        else:
            print "- executing command: " + command
            if print_only is False:
                outputfile = open(outputfilepath, 'w')
                subprocess.call(command.split(), cwd='./data/tabix_indexes/', stdout=outputfile)
                subprocess.call(["gzip", "-f", outputfile.name])

        # Calculate how many SNPs correspond to the gene, and update Table S1
        gene_length = int(end) - int(start)
        report_table_content += "{0}\t{1}\n".format('\t'.join(fields), gene_length)
        

    return report_table_content

def main():
    (genes, options) = get_options()
    report_table_content = get_genotypes(genes, options.baseurl, options.force_index, options.force_download, options.get_individuals, options.flank, options.outputpath, options.onlyprint)
    print report_table_content
    pathway = options.genes.split('/')[-1].rsplit('.')[0]
#    report_outputfilepath = options.report_outputpath
#    report_outputfile = open(report_outputfilepath, 'w')
#    report_outputfile.write(report_table_content)


if __name__ == '__main__':
    import logging
    import doctest
    logging.basicConfig(level=logging.DEBUG)
    doctest.testmod()
    main()
