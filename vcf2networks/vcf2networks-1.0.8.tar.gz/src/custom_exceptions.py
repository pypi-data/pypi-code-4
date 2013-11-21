#!/usr/bin/env python
"""
This file contains exceptions raised by the VCF2Networks project
"""
import os
class InvalidIndividualsFile(Exception):
    def __init__(self, message, individuals_file):
        print 
        print "ERROR: The Individuals file provided with the --individuals option is invalid, or missing."
        print "\nMore details on the error:                \n\t" + message + '\n'
        print "This is the individuals_file that you provided with the --individuals option:\n\t'" + individuals_file + "'"
        print 
        print "Please use vcf2networks --help to get usage information"
        print
#        print "\n\nPlease use vcf2networks --help to get usage information"
        print """\nThis is an example of how the individuals_file should look like:

    #ID         POP     CONTINENT       PHENOTYPE1
    HG00096	GBR	EUR	        pink
    HG00097	GBR	EUR	        blue
    HG00099	GBR	EUR	        blue
    HG00100	GBR	EUR	        pink
    HG00101	GBR	EUR	        blue
    HG00102	GBR	EUR	        blue
    HG00103	GBR	EUR	        pink
    HG00104	GBR	EUR	        blue
    HG00106	GBR	EUR	        blue
    HG00108	GBR	EUR	        pink
    ...........
    
    """

        if os.path.isfile(individuals_file): 
            print "These are the first lines of your individuals_file, {0}:".format(individuals_file)
            indfile = open(individuals_file, 'r')
            for x in range(11):
                print '    ' + indfile.readline(), 
#            for line in firstlines:
#                print "\t" + line,

        print "\nCheck that your individuals_file respects the correct format, and that all individuals are defined."
        print "\nCheck also our tutorial at https://bitbucket.org/dalloliogm/vcf2networks for other examples.\n\n\n"

class InvalidPhenotype(Exception):
    def __init__(self, message, individuals_file, phenotype):
        print 
        print "ERROR: The phenotype specified does not exists."
        print "\nMore details on the error:                \n\t" + message + '\n'
        print "This is the individuals_file that you provided with the --individuals option:\n\t'" + individuals_file + "'"
        print "This is the phenotype you requested:\n\t'" + phenotype + "'"
        print 
        print "Please use vcf2networks --help to get usage information"
        print
        if os.path.isfile(individuals_file): 
            print "These are the first lines of your individuals_file, {0}. There it should be a column named '{1}'.".format(individuals_file, phenotype)
            indfile = open(individuals_file, 'r')
            for x in range(11):
                print '    ' + indfile.readline(), 
#            for line in firstlines:
#                print "\t" + line,

        print "\nCheck that your individuals_file respects the correct format, and that all individuals are defined."
        print "\nCheck also our tutorial at https://bitbucket.org/dalloliogm/vcf2networks for other examples.\n\n\n"




class GenotypeNetworkInitError(Exception):
    """error raised when something went wrong with Network initialization,
    such as an improper genotype string or a wrong parameter"""
    def __init__(self, message=""):
        print "ERROR: an error occurred when initializing the Genotype Network. Probably one of the input file is not formatted properly."
        print
        print message

class GenotypeNetworkAttributeError(Exception):
    """error raised when something tried to access to an attribute
    of the genotype network that doesn't exists"""
    def __init__(self, message=""):
        print "ERROR: " + message











if __name__ == '__main__':
    pass

