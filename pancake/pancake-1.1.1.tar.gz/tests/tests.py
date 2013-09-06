import os
import sys
from Bio import SeqIO,Entrez
import cProfile

_libdir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../')
if os.path.isfile(os.path.join(_libdir, 'pancake', '__init__.py')):
	sys.path.insert(0, _libdir)

from pancake.pangenome import PanGenome,decompress
from pancake.__init__ import *


def test_sequences():
	pan_file = 'tests/test.pan'
	seq_dict = {}
	create([], ["372102604", '38231477', '372116212'], email=None, pan_file=pan_file)
	pangenome=decompress(pan_file)
	for chrom in pangenome.chromosomes:
		seq_dict[chrom.name] = pangenome.seq(chrom)
	add_alignments(pan_file, ['tests/out.delta'], pan_file, min_len=100, self_alis=False)
	pangenome=decompress(pan_file)
	for chrom in pangenome.chromosomes:
		assert pangenome.seq(chrom) == seq_dict[chrom.name], 'Error in test_sequences after alignment inegration! {}'.format(chrom.name)
	pangenome.compress(pan_file)
	include_genome_info(pan_file, 'tests/genomes.txt')


if __name__ == "__main__":
	pass
