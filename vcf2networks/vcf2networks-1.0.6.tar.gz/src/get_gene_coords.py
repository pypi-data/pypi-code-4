#!/usr/bin/env python
"""
Get chromosome coordinates from UCSC tables

Usage:

    python get_gene_coords.py -l genes.txt -d hg19

genes.txt is a file containing a list of Gene Ids to be retrieved, one per line.

Reference: http://biostar.stackexchange.com/questions/3121/genomic-cordinates-from-ucsc

Script taken from another repository: https://bitbucket.org/dalloliogm/ucsc-fetch
"""

import subprocess
#import sys
import logging
import optparse

def get_options():
    parser = optparse.OptionParser(usage="python {} -l genes.txt -d hg19".format(__file__), description=__doc__)
    parser.add_option('-l', '-g', '-f', '--list', '--list_of_genes', '--genes', dest='genes', 
            help='file containing the list of gene. One symbol per line', default=False)
    parser.add_option('-d', '--database', dest='database',
            help='database version (e.g. hg18 or hg19). Default: hg19', default='hg19')
    parser.add_option('-u', '--debug', dest='debug', action='store_true', default=True)
    (options, args) = parser.parse_args()
    
    if options.debug is True:
        logging.basicConfig(level=logging.DEBUG, filename='logs/get_gene_coords.log')

    if (options.genes is False) and (len(args) == 0):
        parser.print_help()
        parser.error('get_gene_coords.py: genes file not defined.')
#    print args
#    print options.genes
    try:
        genes_path = ''
        if options.genes is not False:
            genes_path = options.genes
        elif args != '':
            genes_path = args[0]
#        print genes_path
#        if genes_path != '':
#            genes_h = open(genes_path, 'r')
    except:
        print __doc__
        parser.error("Can not open genes file")

    (genes, gene_order) = read_genes_file(genes_path)
    logging.debug(genes)

    return (genes, gene_order, options.database)

def read_genes_file(genes_path):
    """
    Read a genes file and returns a list of lists
    
    Example genes file
    ----------------------

    ..
        
        #gene    pathway subpathway
        DPAGT1  glycosylation   precursor
        ALG2  glycosylation   precursor
        ALG1  glycosylation   precursor


    Example output list
    -------------------

    ..
        [ 
            ("DPAGT1", "glycosylation", "precursor"),
            ("ALG2", "glycosylation", "precursor"),
            ("ALG1", "glycosylation", "precursor"),
        ]
    """
    genes = {}
    gene_order = []
    with open(genes_path) as genes_h:
        for line in genes_h:
#            print 'line "' + line.strip() + '"' 
            if not line.strip() == '' and not line.startswith('#'):
                fields = line.split()
                gene_name = fields[0]
                if genes.has_key(gene_name):
                    raise ValueError("Duplicated line in gene list file {0}".format(genes_path))
                genes[gene_name] = tuple(fields)
                gene_order.append(gene_name)
#    print genes
    return genes, gene_order

def query_ucsc(genes, gene_order, database):
    """
    Query UCSC MySQL database to get coordinates of a list of genes.

    Print results to STDOUT
    """
    # QUERYING UCSC
    genes_str = '("' + '", "'.join([gene for gene in genes.keys()]) + '")'
    command = """mysql  -h  genome-mysql.cse.ucsc.edu -A -u genome -D %s -e 'select distinct X.geneSymbol,G.chrom,G.txStart,G.txEnd from knownGene as G join kgXref as X on X.kgId=G.name where X.geneSymbol in %s ' """ % (database, genes_str)
#    command = """mysql  -h  genome-mysql.cse.ucsc.edu -A -u genome -D %s -e 'select distinct K.geneSymbol,G.chrom,G.txStart,G.txEnd from refGene as G join kgXref as X on X.kgId=G.name2 where X.geneSymbol in %s ' """ % (database, genes_str)
    logging.debug(command)

    # PARSING RESULTS to remove redundant entries (TODO: use Mysql function)

    # I don't have a recent version of the subprocess installed, so instead of subprocess.check_output I have to use a temporary file.
    temp_output = subprocess.check_output(command, shell=True)

    all_genes = {}
    for line in temp_output.split('\n')[1:]:
#        print "line: '" + line + "'", line.strip() == ''
        if not line.strip() == '':
#            print "line", line
            (gene, chrom, start, end) = line.split()
            (name, pathway, subpathway) = genes[gene]
#            print name, pathway, subpathway
            start = int(start)
            end = int(end)
#            logging.debug(start < end)
            if not all_genes.has_key(gene):
                all_genes[gene] = [gene, pathway, subpathway, chrom, start, end]
            else:
                if start < all_genes[gene][4]:
                    logging.debug((gene, "(start)", start, all_genes[gene][4]))
                    all_genes[gene][4] = start

                if end > all_genes[gene][5]:
                    logging.debug((gene, "(end)", end, all_genes[gene][5]))
                    all_genes[gene][5] = end

    # PRINTING OUTPUT

#    for (gene, values) in all_genes.items():
    for gene_name in gene_order:
        if all_genes.has_key(gene_name):
            values = all_genes[gene_name]
            print '%s\t%s\t%s\t%s\t%s\t%s' % tuple(values)
        else:
            logging.warning("Could not find coordinates for gene {}".format(gene_name))
#    print ("output saved to {}".format(outputfile))

def main():
    (genes, gene_order, database) = get_options()
#    print genes, database
    query_ucsc(genes, gene_order, database)

if __name__ == '__main__':
    main()

