#!/usr/bin/env python
"""
Test the get_genotypes script, to download vcf files from 1000genomes
"""
import subprocess
import os
import logging
import nose

@nose.plugins.attrib.attr('internet')
def test_SimpleSetOfGenes():
    coordsfile = 'test/test_data/coords/n-glycan.coords'
    expected_outputfiles = "test/test_data/vcf/ALG11.vcf.gz test/test_data/vcf/NRG3.vcf.gz".split()
    logging.debug( "rm {0}".format(" ".join(expected_outputfiles)))
    output = subprocess.check_output("rm -f {0}".format(" ".join(expected_outputfiles)).split())

    com = "python src/get_genotypes.py --coordinates_file {0} --outputpath test/test_data/vcf/ --flank 10000 --force-download --report_output test/test_data/vcf/n_snps_report.txt".format(coordsfile)
    output = subprocess.check_output(com.split())
    for f in expected_outputfiles:
        yield check_file_exists, f
    

def check_file_exists(f):
    assert os.stat(f).st_size > 0


if __name__ == '__main__':
    import logging
    import doctest
    logging.basicConfig(level=logging.DEBUG)
    doctest.testmod()


