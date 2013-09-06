import os
import sys

from Bio import SeqIO,Entrez
from pancake.pangenome import PanGenome, decompress
from pancake.aliparser import parse_alis
from pancake.core import get_genome_core,get_core,write_core_fasta_files
from pancake.singletons import get_genome_singletons,get_singletons
from pancake.gv_graphs import get_gv


__author__ = "Corinna Ernst"
__version__ = "1.1"


def create(files, identifiers, email, pan_file=None, alis=None, min_len=25, self_alis=True):

	if not pan_file:
		pan_file = os.getcwd() + '/pan_files/pancake.pan'
		dir = os.path.dirname(pan_file)
		try:
			os.stat(dir)
		except:
			os.mkdir(dir)
	else:
		dir, f = os.path.split(pan_file)
		if dir:
			try:
				os.stat(dir)
			except:
				os.mkdir(dir)
	
	pangenome = PanGenome()
	if files:
		for f in files:
			records = list(SeqIO.parse(open(f, 'r'), "fasta"))
			for record in records:
				pangenome.add_chromosome(str(record.name), seq=str(record.seq))
	if identifiers:
		if email: Entrez.email=email
		for identifier in identifiers:
			handle = Entrez.efetch(db="nucleotide", id=identifier, rettype="fasta", retmode="text")
			record = SeqIO.read(handle, "fasta")
			handle.close()
			pangenome.add_chromosome(str(record.name), seq=str(record.seq).upper())
	sys.stderr.write('#\n...pangenome initialized\n')
	try:
		pangenome.compress(pan_file)
	except:
		sys.stderr.write('Error while pangenome compressing\n')
	if alis:
		for ali_file in alis:
			sys.stderr.write('#\n')
			pangenome = parse_alis(ali_file, pangenome, min_len, self_alis)
			sys.stderr.write('#\n')
			sys.stderr.write('...check for non-similarity SFs\n')
			pangenome.check_non_similarity()
			sys.stderr.write('...downgrade non-aligned Feature Instances\n')
			pangenome.refine_unlabeled()
			sys.stderr.write('...concatenate Shared Features\n')
			pangenome.refine_adjacent_sfs()
			try:
				pangenome.compress(pan_file)
			except:
				sys.stderr.write('Error while pangenome compressing\n')
	statinfo = os.stat(pan_file)
	sys.stderr.write('...PanCake Object written to {} ({} bytes)\n'.format(pan_file, statinfo.st_size))


def add_alignments(pan_file, alis, output, min_len, self_alis=True):

	dir, f = os.path.split(output)
	if dir:
		try:
			os.stat(dir)
		except:
			os.mkdir(dir)

	try:
		pangenome=decompress(pan_file)
	except:
		sys.stderr.write('...unable to initialize pangenome from {}!\n'.format(pan_file))
		return
	sys.stderr.write('...pangenome loaded from {}\n'.format(pan_file))
	for ali_file in alis:
		sys.stderr.write('#\n')
		try:
			pangenome = parse_alis(ali_file, pangenome, min_len, self_alis)
		except:
			sys.stderr.write('Error while parsing {}.\n'.format(ali_file))
		sys.stderr.write('#\n')
		sys.stderr.write('...check for non-similarity SFs\n')
		pangenome.check_non_similarity()
		sys.stderr.write('...downgrade non-aligned Feature Instances\n')
		pangenome.refine_unlabeled()
		sys.stderr.write('...concatenate Shared Features\n')
		pangenome.refine_adjacent_sfs()
		sys.stderr.write('#\n')
		
		try:
			pangenome.compress(output)
		except:
			sys.stderr.write('Error while pangenome compressing\n')
	statinfo = os.stat(output)
	sys.stderr.write('...PanCake Object written to {} ({} bytes)\n'.format(output, statinfo.st_size))


def core(pan_file, ref_chrom, ref_genome, min_len, genomes=[], chroms=[], exclude_genomes=[], exclude_chromosomes=[], non_core_frac=0.1, nc_space=25, folder=None, output=True, bed_file=''):
	try:
		pangenome=decompress(pan_file)
	except:
		sys.stderr.write('...unable to initialize pangenome from {}!\n'.format(pan_file))
		return
	if ref_chrom:
		if not bed_file: bed_file = 'core_{}.bed'.format(ref_chrom)
		open(bed_file, 'w').close()
		print('#\n...parsing ' + ref_chrom)
		regions = get_core(pangenome, ref_chrom, min_len, genomes, chroms, exclude_genomes, exclude_chromosomes, non_core_frac, nc_space, {},bed_file)
	elif ref_genome:
		if not bed_file: bed_file = 'core_{}.bed'.format(ref_genome)
		open(bed_file, 'w').close()
		regions = get_genome_core(pangenome, ref_genome, min_len, genomes, chroms, exclude_genomes, exclude_chromosomes, non_core_frac, nc_space, bed_file)
	if output:
		if not folder: 
			folder = 'core_'+ ref_chrom if ref_chrom else 'core_'+ ref_genome
		write_core_fasta_files(pangenome, regions, ref_chrom, folder)


def singletons(pan_file, ref_chrom, ref_genome, min_len, genomes=[], chroms=[], exclude_genomes=[], exclude_chromosomes=[], outfolder='', output=True, bed_file=''):
	try:
		pangenome=decompress(pan_file)
	except:
		sys.stderr.write('...unable to initialize pangenome from {}!\n'.format(pan_file))
		return
	if ref_chrom:
		if not bed_file: bed_file = 'singletons_{}.bed'.format(ref_chrom)
		open(bed_file, 'w').close()
		get_singletons(pangenome, ref_chrom, min_len, genomes, chroms, exclude_genomes, exclude_chromosomes, outfolder, output, bed_file)
	elif ref_genome:
		if not bed_file: bed_file = 'singletons_{}.bed'.format(ref_genome)
		open(bed_file, 'w').close()
		get_genome_singletons(pangenome, ref_genome, min_len, genomes, chroms, exclude_genomes, exclude_chromosomes, outfolder, output, bed_file)


def stats(pan_file):
	try:
		pangenome=decompress(pan_file)
	except:
		sys.stderr.write('...unable to initialize pangenome from {}!\n'.format(pan_file))
		return
	ul = 0
	ul_dict = {}
	for chrom in pangenome.chromosomes:
		ul+=len(pangenome.unlabeled[chrom])
		ul_dict[chrom] = len(pangenome.unlabeled[chrom])
	l, s = 0, 0
	for f in pangenome.features:
		l+= len(f.entries)
		s+=1
	print('\nPanGenome Object consists of {} un-aligned FIs & {} aligned FIs (organized in {} Shared Features)'.format(ul, l, s))
	print('#\n{} chromosomes representing {} genomes, namely:'.format(len(pangenome.chromosomes), len(pangenome.genomes)))
	#chromosome information
	for genome in pangenome.genomes:
		print('#\nGenome '+str(genome))
		for chrom in pangenome.genomes[genome]:
			ref_name = chrom.name
			names=set()
			for name in pangenome.chrom_names:
				if pangenome.chrom_names[name] == chrom and name != chrom.name: names.add(name)
			if names: 
				print('>'+ref_name + ', ' + ', '.join(list(names)) + ' ('+ str(pangenome.chrom_length(chrom)) +'bp)')
			else: print('>'+ref_name + ' ('+ str(pangenome.chrom_length(chrom)) +'bp)')
			l, l_length,sf_set = set(), 0, set()
			ul_length, ul = 0,0
			fi = pangenome.chromosomes[chrom][1]
			while fi:
				if fi.sh_feat:
					l.add(fi)
					l_length += (fi.stop-fi.start+1)
					sf_set.add(fi.sh_feat)
				else:
					ul_length += (fi.stop-fi.start+1)
					ul +=1
				fi=fi.nextFI
			if ul:
				print('--> {} un-aligned Feature Instances (mean length {})'.format(ul, ul_length/ul))
			else:
				print('--> {} un-aligned Feature Instances (mean length {})'.format(ul, 0))
			if l:
				print('--> {} aligned Feature Instances (mean length {}) in {} Shared Features'.format(len(l), l_length/len(l), len(sf_set)))
			else:
				print('--> {} aligned Feature Instances (mean length {}) in {} Shared Features'.format(0, 0, 0))


def add_chromosomes(panfile, files, ids, email='', outfile='', alis=None, min_len=25, self_alis=True):
	try:
		pangenome = decompress(panfile)
	except:
		raise ValueError('...unable to open {}!'.format(panfile))

	if outfile != panfile:
		dir, f = os.path.split(outfile)
		if dir:
			try:
				os.stat(dir)
			except:
				os.mkdir(dir)
	
	if files:
		for f in files:
			records = list(SeqIO.parse(open(f, 'r'), "fasta"))
			for record in records:
				pangenome.add_chromosome(str(record.name), seq=str(record.seq))
	if ids:
		if email: Entrez.email=email
		for identifier in ids:
			handle = Entrez.efetch(db="nucleotide", id=identifier, rettype="fasta", retmode="text")
			record = SeqIO.read(handle, "fasta")
			handle.close()
			pangenome.add_chromosome(str(record.name), seq=str(record.seq).upper())
	sys.stderr.write('#\n...chromosome(s) added\n')
	if alis:
		for ali_file in alis:
			sys.stderr.write('#\n')
			pangenome = parse_alis(ali_file, pangenome, min_len, self_alis)
			sys.stderr.write('#\n')
			sys.stderr.write('...check for non-similarity SFs\n')
			pangenome.check_non_similarity()
			sys.stderr.write('...downgrade non-aligned Feature Instances\n')
			pangenome.refine_unlabeled()
			sys.stderr.write('...concatenate Shared Features\n')
			pangenome.refine_adjacent_sfs()
			sys.stderr.write('Error while SF concatenation.\n')
			sys.stderr.write('#\n')
	try:
		pangenome.compress(outfile)
	except:
		sys.stderr.write('Error while pangenome compressing\n')
	statinfo = os.stat(outfile)
	sys.stderr.write('...PanCake Object written to {} ({} bytes)\n'.format(outfile, statinfo.st_size))


def delete_name(panfile, names):
	try:
		pangenome = decompress(panfile)
	except:
		raise ValueError('...unable to open {}!'.format(panfile))
	for name in names:
		try:
			chrom = pangenome.chrom_names[name]
			chrom_names=list(filter(lambda x: pangenome.chrom_names[x]==chrom, pangenome.chrom_names))
			if len(chrom_names) == 1:
				sys.stderr.write('...{} is exclusive chromosome name! Specify new name before deletion!\n'.format(name))
			else:
				del pangenome.chrom_names[name]
				chrom_names.remove(name)
				if chrom.name == name: chrom.name = chrom_names[0]
		except:
			sys.stderr.write('...unable to find chromosome name {} in {}! ...SKIPPING\n'.format(name, panfile))
	try:
		pangenome.compress(panfile)
	except:
		sys.stderr.write('Error while pangenome compressing\n')

def new_name(panfile, chrom_name, new_name):
	try:
		pangenome = decompress(panfile)
	except:
		raise ValueError('...unable to open {}!'.format(panfile))
		
	if chrom_name not in pangenome.chrom_names: 
		raise ValueError('Chromosome {} could not be found in PanCake Data Object from file {}!'.format(chrom_name, panfile))

	chrom = pangenome.chrom_names[chrom_name]
	genome_flag = chrom_name == chrom.genome
	chrom.new_name(new_name)
	pangenome.chrom_names[new_name] = chrom
	if genome_flag and chrom_name in pangenome.genomes and len(pangenome.genomes[chrom_name])==1:
		del pangenome.genomes[chrom_name]
		pangenome.genomes[new_name] = set()
		pangenome.genomes[new_name].add(chrom)
		chrom.genome = new_name
	try:
		pangenome.compress(panfile)
	except:
		sys.stderr.write('Error while pangenome compressing\n')

def add_to_genome(panfile, chroms, genome):
	try:
		pangenome = decompress(panfile)
	except:
		raise ValueError('...unable to open {}!'.format(panfile))
	for chrom_name in chroms:
		chrom = pangenome.chrom_names[chrom_name]
		pangenome.genomes[chrom.genome].remove(chrom)
		if len(pangenome.genomes[chrom.genome]) == 0: del pangenome.genomes[chrom.genome]
		chrom.genome = genome
		if genome not in pangenome.genomes:
			pangenome.genomes[genome] = set()
		pangenome.genomes[genome].add(chrom)
	try:
		pangenome.compress(panfile)
	except:
		sys.stderr.write('Error while pangenome compressing\n')

def include_genome_info(panfile, genome_file):
	'''specifyChrom: include information from genome file provided by the user'''
	try:
		pangenome = decompress(panfile)
	except:
		raise ValueError('...unable to open {}!'.format(genome_file))
	try:
		pangenome = decompress(panfile)
	except:
		raise ValueError('...unable to open {}!'.format(genome_file))
	with open(genome_file) as genomes:
		for line in genomes:
			ll = line.strip().split('\t')
			if len(ll)>1:
				genome = ll[0]
				chrom_name = ll[1]
				#change chromosome name
				if len(ll)==3: 
					new_name = ll[2]
					chrom = pangenome.chrom_names[chrom_name]
					genome_flag = True if chrom_name == chrom.genome else False
					chrom.new_name(new_name)
					pangenome.chrom_names[new_name] = chrom
					if genome_flag and chrom_name in pangenome.genomes and len(pangenome.genomes[chrom_name])==1:
						del pangenome.genomes[chrom_name]
						pangenome.genomes[new_name] = set()
						pangenome.genomes[new_name].add(chrom)
						chrom.genome = new_name
					chrom_name = new_name
				try:
					chrom = pangenome.chrom_names[chrom_name]
					pangenome.genomes[chrom.genome].remove(chrom)
					if len(pangenome.genomes[chrom.genome]) == 0: del pangenome.genomes[chrom.genome]
					chrom.genome = genome
					if genome not in pangenome.genomes:
						pangenome.genomes[genome] = set()
					pangenome.genomes[genome].add(chrom)
				except:
					sys.stderr.write('Chromosome {} not in pangenome!\n'.format(chrom_name))
	try:
		pangenome.compress(panfile)
	except:
		sys.stderr.write('Error while pangenome compressing\n')


def sequence(panfile, genome_name, chrom_name, start, stop, outfile='', lw=100):
	try:
		pangenome = decompress(panfile)
	except:
		raise ValueError('...unable to open {}!'.format(panfile))
	
	if chrom_name:
		try:
			chrom= pangenome.chrom_names[chrom_name] 
		except:
			raise ValueError('Chromosome {} could not be found in PanCake Object from file {}!'.format(chrom_name, panfile))
	
		chrom_length = pangenome.chrom_length(chrom)
		if start> chrom_length:
			raise ValueError('Specified START position {} > length of chromosome {} ({}bp)!'.format(start, chrom, chrom_length))

		if not stop:
			stop = chrom_length
		elif stop > chrom_length:
			raise ValueError('Specified STOP position > length of chromosome {} ({}bp)!'.format(stop, chrom, chrom_length))
	
		#get sequence
		seq = pangenome.seq(chrom,start, stop)
		if outfile:
			fasta_header = '>{} {}-{} ({}bp)\n'.format(chrom_name, start, stop, stop-start+1)
			seq='\n'.join(seq[i:i+lw] for i in range(0, len(seq), lw)) + '\n' #insert linebreaks
			dir, f = os.path.split(outfile)
			if dir:
				try:
					os.stat(dir)
				except:
					os.mkdir(dir)
		
			with open(outfile, 'wt') as fasta_file:
				fasta_file.write(fasta_header)
				fasta_file.write(seq)
		else:
			print(seq)
	elif genome_name:
		try:
			chroms = pangenome.genomes[genome_name]
		except:
			raise ValueError('Genome {} could not be found in PanCake Object from file {}!'.format(genome_name, panfile))
		chroms = sorted(list(chroms), key= lambda x: pangenome.chromosome_stops[x].stop, reverse=True)
		if outfile:
			dir, f = os.path.split(outfile)
			if dir:
				try:
					os.stat(dir)
				except:
					os.mkdir(dir)
			open(outfile, 'w').close()
		for chrom in chroms:
			stop = pangenome.chromosome_stops[chrom].stop
			fasta_header = '>{} {}-{} ({}bp)\n'.format(chrom.name, 1, stop, stop)
			seq = pangenome.seq(chrom)
			seq='\n'.join(seq[i:i+lw] for i in range(0, len(seq), lw)) + '\n' #insert linebreaks
			if outfile:
				with open(outfile, 'at') as fasta_file:
					fasta_file.write(fasta_header)
					fasta_file.write(seq)
			else:
				print(fasta_header)
				print(seq)



def initialize_gv_output(pan_file, chroms, starts, stops, all_flag, region_flag, max_entries, max_nodes, max_edges, output):

	#open panfile
	try:
		pangenome=decompress(pan_file)
	except:
		sys.stderr.write('#\n...unable to initialize pangenome from {}!\n'.format(pan_file))
		return
	sys.stderr.write('#\n...pangenome loaded from {}\n#\n'.format(pan_file))
	
	final_chroms, final_starts, final_stops = [], [], []
	
	if not chroms:
		sys.stderr.write('...no chromosomes specified ...taking all chromosomes from {}\n'.format(pan_file))
		final_chroms = list(pangenome.chromosome_stops.keys())
	else:
		for i in range(len(chroms)):
			try:
				chrom = pangenome.chrom_names[chroms[i]]
			except:
				raise ValueError('Chromosome {} could not be found in PanCake Object from file {}!'.format(chroms[i], pan_file))
			final_chroms.append(chrom)
	for i in range(len(final_chroms)):
		chrom_len = pangenome.chrom_length(final_chroms[i])
		#treat start
		if starts and i<len(starts) and starts[i]:
			if starts[i] < 1:
				sys.stderr.write('...START position {} on chromosome {} <1 ...setting to 1\n'.format(starts[i], final_chroms[i]))
				starts[i] = 1
			elif starts[i] > chrom_len:
				sys.stderr.write('...START position {} on chromosome {} > chromosome length {}bp ...setting to chromosome length\n'.format(starts[i], final_chroms[i], chrom_len))
				starts[i] = chrom_len
			final_starts.append(starts[i])
		else: final_starts.append(1)
		#treat stop
		if stops and i<len(stops) and stops[i]:
			if stops[i] < final_starts[i]:
				sys.stderr.write('...STOP position {} on chromosome {} < start position {} ...setting to chromosome length {}bp\n'.format(stops[i], final_chroms[i], final_starts[i], chrom_len))
				stops[i] = chrom_len
			elif stops[i] > chrom_len:
				sys.stderr.write('...STOP position {} on chromosome {} > chromosome length {}bp ...setting to chromosome length\n'.format(stops[i], final_chroms[i], chrom_len))
				stops[i] = chrom_len
			final_stops.append(stops[i])
		else: final_stops.append(chrom_len)

	sys.stderr.write('#\n...creating .gv file covering\n')
	for i in range(len(final_chroms)):
		sys.stderr.write('{}\t{}-{}\n'.format(final_chroms[i], final_starts[i], final_stops[i]))
	sys.stderr.write('#\n')
	get_gv(pangenome, final_chroms, final_starts, final_stops, all_flag,region_flag, max_entries, max_nodes, max_edges, output)



#DEBUG
#def printer(panfile):
#	try:
#		pangenome = decompress(panfile)
#	except:
#		raise ValueError('...unable to open {}!'.format(panfile))
#	print(pangenome)
