import sys,os
from collections import defaultdict

####SINGLETONS

def get_genome_singletons(pancake, ref_genome, min_len, genomes, chromosomes, exclude_genomes, exclude_chromosomes, folder='', output=True, bed_file=''):
	#very much simplified in contrast to core search, just get the set of all chromosomes not allowed to be aligned with
	if ref_genome not in pancake.genomes:
		raise ValueError('Genome ' + str(ref_genome) + ' not in PanGenome!')
	else:
		ref_chroms = pancake.genomes[ref_genome]
	for chrom in ref_chroms:
		print('#\n...parsing {}'.format(chrom), file=sys.stderr)
		regions = get_singletons(pancake, chrom.name, min_len, genomes, chromosomes, exclude_genomes, exclude_chromosomes, folder, output, bed_file)
	return regions

def get_singletons(pancake, ref_chrom, min_len, chroms=[], genomes=[], exclude_genomes=[], exclude_chromosomes=[], folder='', output=True, bed_file=''):

	#initiation, error checking
	if ref_chrom not in pancake.chrom_names:
		raise ValueError('Chromosome ' + str(ref_chrom) + ' not in PanGenome!')
	else:
		ref_chrom =  pancake.chrom_names[ref_chrom]


	if output and not folder:
		folder=os.getcwd() + '/singletons_'+str(ref_chrom)
		try:
			os.stat(folder)
		except:
			os.mkdir(folder)
	elif output:
		try:
			os.stat(folder)
		except:
			os.mkdir(folder)

	#Here: get the set of all chromosomes not allowed to be aligned with ref_chrom
	all_chroms = set()
	if not genomes:
		for g in pancake.genomes:
			if g != ref_chrom.genome:
				for c in pancake.genomes[g]:
					all_chroms.add(c)
	else:
		for g in genomes:
			try:
				tmp_g = pancake.genomes[g]
				all_chroms = all_chroms.union(tmp_g)
			except:
				sys.stderr.write('...genome {} not in pangenome! ...SKIPPING\n'.format(g))

	for c in chroms:
		try:
			all_chroms.add(pancake.chrom_names[c])
		except:
			sys.stderr.write('...chromosome {} not in pangenome! ...SKIPPING\n'.format(c))
	if ref_chrom in all_chroms: all_chroms.remove(ref_chrom)

	for c in exclude_chromosomes:
		try:
			chrom = pancake.chrom_names[c]
			if chrom in all_chroms: all_chroms.remove(chrom)
		except:
			sys.stderr.write('...chromosome {} not in pangenome! ...SKIPPING\n'.format(c))
	for g in exclude_genomes:
		try:
			tmp_g = pancake.genomes[g]
			for c in tmp_g:
				if c in all_chroms: all_chroms.remove(c)
		except:
			sys.stderr.write('...genome {} not in pangenome! ...SKIPPING\n'.format(g))

	fi = pancake.chromosomes[ref_chrom][1] #current fi
	regions = list() #list of tuples
	min_length, max_length, m = 0,0,0
	with open(bed_file, 'a') as bedfile:
	#iterate over reference genome
		while fi:
			if not fi.sh_feat or fi.sh_feat.singleton_sf(all_chroms):
				if regions and regions[-1][1] +1 == fi.start:
					regions[-1] = (regions[-1][0], fi.stop)
				else:
					regions.append((fi.start, fi.stop))
			fi = fi.nextFI 
		count, l = 0, 0
		if regions:
			min_length, max_length = None, None
			for region in regions:
				region_length = region[1]-region[0]+1
				if region_length >= min_len:
					bedfile.write('{}\t{}\t{}\n'.format(ref_chrom, region[0], region[1]))
					if output:
						with open('{}/{}_{}-{}.fa'.format(folder, ref_chrom, region[0], region[1]), 'wt') as fasta:
							fasta.write('>{} {}-{} ({}bp)\n'.format(ref_chrom, region[0], region[1], region[1]-region[0]+1))
							fasta.write(pancake.seq(ref_chrom, region[0], region[1]) + '\n')
					count+=1
					l+=region_length
					if not min_length or region_length < min_length: min_length = region_length
					if not max_length or region_length > max_length: max_length = region_length
		sys.stderr.write('#\n')
		if count >0:
			print('Found {} singleton regions.\nMinimum Length = {}\nMaximum Length = {}\nMean = {}\n'.format(count, min_length, max_length, l/count))
			if output:
				print('Singleton regions written into folder {}'.format(folder))
		else:
			print('Found NO singleton regions.')
