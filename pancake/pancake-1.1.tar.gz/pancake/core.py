import sys,os
from collections import defaultdict
from pancake.utils import rev_comp

####CORE Identification

def get_genome_core(pancake, ref_genome, min_len, genomes, chroms, exclude_genomes, exclude_chromosomes, non_core_frac, nc_space, bed_file):
	#get all chromosomes of ref_genome
	if ref_genome not in pancake.genomes:
		raise ValueError('Genome ' + str(ref_genome) + ' not in PanGenome!')
	else:
		ref_chroms = set([x.name for x in pancake.genomes[ref_genome]])
	regions=dict()
	#compute excludes: all chromosomes of ref_genome
	exclude_chromosomes = set(exclude_chromosomes).union(ref_chroms)
	for chrom in ref_chroms:
		print('#\n...parsing {}'.format(chrom), file=sys.stderr)
		regions = get_core(pancake, chrom, min_len, genomes, chroms, exclude_genomes, exclude_chromosomes, non_core_frac, nc_space, regions, bed_file)
	return regions


#get core for 1 chromosome; called nchromosomes-times if ref_genome is specified
def get_core(pancake, ref_chrom, min_len, genomes=[], chromlist=[], exclude_genomes=[], exclude_chromosomes=[], non_core_frac=0.1, nc_space=25, regions=dict(), bed_file='core.bed'):

	#initiation, error checking
	if ref_chrom not in pancake.chrom_names:
		raise ValueError('Chromosome ' + str(ref_chrom) + ' not in PanGenome!')
	else:
		ref_chrom =  pancake.chrom_names[ref_chrom]
	####HERE deal with excludes
	if not genomes:
		genomes = set([x.genome for x in pancake.chromosomes])
	else:
		genomes = set(genomes)
	if ref_chrom.genome in genomes: genomes.remove(ref_chrom.genome)
	
	chroms = set()
	tmp_genomes = set()
	for chrom in chromlist: 
		if chrom not in pancake.chrom_names: 
			raise ValueError('Chromosome ' + str(chrom) + ' not in PanGenome!')
		chrom = pancake.chrom_names[chrom]
		chroms.add(chrom)
		if chrom.genome in genomes: 
			tmp_genomes.add(chrom.genome)
	genomes = genomes.difference(tmp_genomes)
	genomes = genomes.difference(set(exclude_genomes))

	exclude_dict = defaultdict(set)
	for chrom in exclude_chromosomes:
		if chrom not in pancake.chrom_names: 
			raise ValueError('Chromosome ' + str(chrom) + ' not in PanGenome!')
		chrom = pancake.chrom_names[chrom]
		exclude_dict[chrom.genome].add(chrom)
	for entry in exclude_dict:
		if entry in genomes: genomes.remove(entry)
		for c in pancake.genomes[entry].difference(exclude_dict[entry]):
			chroms.append(c)

	#OUTPUT 
	print('against', file=sys.stderr)
	if genomes:
		print('GENOMES', file=sys.stderr)
		for g in genomes:
			print(' ' + g, file=sys.stderr)
	if chroms:
		print('#\nCHROMOSOMES', file=sys.stderr)
		for c in chroms:
			print( ' ' + str(c), file=sys.stderr)
	print('#', file=sys.stderr)
	###END OUTPUT

	#identify core FIs and core SFs
	fi = pancake.chromosomes[ref_chrom][1]
	core_fis = []
	l=0
	core_sfs = []
	while fi:
		if fi.sh_feat: 
			if fi.sh_feat in core_sfs:
				core_fis.append(fi)
				l+=1
			elif core_sf(fi, genomes, chroms):
				core_fis.append(fi)
				core_sfs.append(fi.sh_feat)
				l+=1
		fi=fi.nextFI
	print('Found {} core FIs!\n#'.format(l), file=sys.stderr)


	regions[ref_chrom] = dict()
	starts=list()
	min_length, max_length, m = 0,0,0
	#iterate over reference genome
	fi_count, core_fi_count = 0, 0
	with open(bed_file, 'a') as bedfile:

		for i in range(len(core_fis)):
			if i != 0 and i%1000 == 0:
				print('...{} Feature Instances parsed (current chromosome position = {})'.format(i, core_fis[i].start))
			region = get_region(i, core_fis, pancake, genomes, chroms, non_core_frac, nc_space)
			fi = core_fis[i]
			#decide here if add to regions
			add_flag = False
			if not starts:
				add_flag =True
			elif starts[-1][1] != region[fi][-1].stop:
				add_flag = True
			ref_tupel = (fi.start, region[fi][-1].stop)
			if ref_tupel[1]-ref_tupel[0]+1 < min_len: add_flag = False
			if add_flag:
				bedfile.write('{}\t{}\t{}\n'.format(ref_chrom, ref_tupel[0], ref_tupel[1]))
				#add to regions (save for output) and include into statistics
				starts.append(ref_tupel)
				l = ref_tupel[1]-ref_tupel[0]+1
				if not min_length or l<min_length: min_length = l
				if not max_length or l>max_length: max_length = l
				m+=l
				regions[ref_chrom][ref_tupel] = dict()#dict of chromosomes (for sorted .fasta output)
				del region[fi]
				for entry in region:
					entry_list = region[entry] #list of core_sfs
					c = entry_list[0].chrom
					if c not in regions[ref_chrom][ref_tupel]: regions[ref_chrom][ref_tupel][c] = list()
					if not entry_list[0].seq.reverse:
						#seq in '+' direction
						regions[ref_chrom][ref_tupel][c].append((entry_list[0].start, entry_list[-1].stop, True))
					else:
						regions[ref_chrom][ref_tupel][c].append((entry_list[-1].start, entry_list[0].stop, False))
	
	if len(starts) >0:
		print('Found ' + str(len(starts)) + ' core regions.\nMinimum Length = '+str(min_length)+'\nMaximum Length = '+ str(max_length) + '\nMean = '+str(m/len(starts))+'\n')#, file=sys.stderr)
	else:
		print('Found NO core regions.')
	return regions


def core_sf(fi, genomes, chromosomes): 
	'''return True if all FIs from genome and chromosomes in fi.sf'''
	#genomes without ref_chrom.genome
	sf = fi.sh_feat
	entries = sf.entries
	l = len(entries)
	if genomes:
		if l < len(genomes):
			return False
		elif not genomes.issubset(set([x.chrom.genome for x in entries])):
			return False
	if chromosomes:
		if l < len(chromosomes):
			return False
		elif not chromosomes.issubset(set([x.chrom for x in entries])):
			return False
	return True


def get_region(j, core_fis, pancake, genomes, chroms, non_core_frac=0.1, nc_space=25):
	'''identifies longest possible core region starting at ref_fi'''
	ref_fi = core_fis[j]
	#initiation
	if ref_fi.seq.reverse: ref_fi.sh_feat.turn()
	region_dic = dict()

	all_chroms = chroms.union(set([ref_fi.chrom]))
	for g in genomes: 
		for c in pancake.genomes[g]:
			all_chroms.add(c)
	for fi in ref_fi.sh_feat:
		if fi.chrom in all_chroms:
			region_dic[fi] = [fi] #sequence of core fis for all chromosomes

	core_flag = True
	ref_space=0
	ref_length=ref_fi.stop-ref_fi.start+1
	#start iteration here
	#find next core_sf for ref_fi
	while core_flag:
		next_ref_core_fi = next_core(j, core_fis, non_core_frac, nc_space, space=ref_space,length=ref_length)
		if next_ref_core_fi:
			j+=1
			#next core_sf found
			ref_space += next_ref_core_fi.start - region_dic[ref_fi][-1].stop +1
			ref_length += next_ref_core_fi.stop - region_dic[ref_fi][-1].stop +1
			region_dic[ref_fi].append(next_ref_core_fi)
			next_core_sf = next_ref_core_fi.sh_feat
			for start_fi in region_dic:
				#iterate over non-reference fis
				if start_fi != ref_fi:
					space=0
					length = start_fi.stop-start_fi.start+1
					next_core_fi = None
					if not start_fi.seq.reverse:
						#go forward through pangenome
						next_fi = region_dic[start_fi][-1].nextFI
						while space/length < non_core_frac and next_fi and not next_core_fi and space <= nc_space:
							if next_fi.sh_feat and next_fi.sh_feat == next_core_sf and not next_fi.seq.reverse:
								next_core_fi = next_fi
							else:
								space += next_fi.stop -next_fi.start+1
								length += next_fi.stop -next_fi.start+1
							next_fi = next_fi.nextFI
					else:
						#go backward through pangenome
						next_fi = region_dic[start_fi][-1].prevFI
						while space/length < non_core_frac and next_fi and not next_core_fi and space <= nc_space:
							if next_fi.sh_feat and next_fi.sh_feat == next_core_sf and next_fi.seq.reverse:
								next_core_fi = next_fi
							else:
								space += next_fi.stop -next_fi.start+1
								length += next_fi.stop -next_fi.start+1
							next_fi = next_fi.prevFI
					region_dic[start_fi].append(next_core_fi)
		else: core_flag = False

		if core_flag==True:
			tmp_chroms = set()
			for fi in region_dic:
				if region_dic[fi][-1]: tmp_chroms.add(fi.chrom)

			#decide if chromosomes still represent a valid core, i.e. one chrom from each genome
			for g in genomes:
				if not pancake.genomes[g].intersection(tmp_chroms):
					core_flag=False
					break
			if core_flag:
				for c in chroms:
					if c not in tmp_chroms: core_flag=False
			
			#not a valid core region any more
			if core_flag == False:
				for fi in region_dic:
					region_dic[fi] = region_dic[fi][:-1]

			else:
				#still a valid core region, but some paths might be cutted
				fi_list = list(region_dic.keys())
				for fi in fi_list:
					if not region_dic[fi][-1]:
						del region_dic[fi]

	return region_dic


def next_core(j, core_fis, non_core_frac, nc_space, space=0,length=0):
	'''return next fi of a core sf fullfilling given constraints, or NONE if there is none'''
	if j+1 < len(core_fis):
		next_fi = core_fis[j+1]
		tmp_space = next_fi.start - core_fis[j].stop -1
		l=next_fi.stop -next_fi.start+1
		if tmp_space < nc_space and (space+tmp_space)/(length+tmp_space+l) <= non_core_frac:
			return next_fi


#CORE .fasta output
def write_core_fasta_files(pancake, regions, ref_genome = None, folder=None, iterator=False):

	if not folder: 
		if ref_genome:
			folder=os.getcwd() + 'core_'+str(ref_chrom)
		elif len(regions)==1:
			folder=os.getcwd() + 'core_'+str(list(regions.keys())[0])
		else:
			folder = os.getcwd() + 'core_regions'
	try:
		os.stat(folder)
	except:
		os.mkdir(folder)

	for ref_chrom in regions.keys():
		starts = list(regions[ref_chrom].keys())
		starts.sort(key = lambda item: item[0], reverse=True)#sort by start value
		other_chroms = list(set(pancake.chromosomes.keys()).difference(set([ref_chrom])))
		core_count =1

		for entry in starts:
			#write .fas file for 1 core region
			with open('{}/{}_{}-{}.fas'.format(folder,ref_chrom,entry[0],entry[1]), 'wt') as fasta:
				#write core sequence of reference chromosome
				fasta.write('>{} {}-{}|len={}bp|+\n'.format(ref_chrom, entry[0], entry[1], entry[1]-entry[0]+1) )
				fasta.write(pancake.seq(ref_chrom, entry[0], entry[1])+'\n')
				#write (possible) other subsequences of reference chromosome
				if ref_chrom in regions[ref_chrom][entry]:
					regions[ref_chrom][entry][ref_chrom].sort(key=lambda item: item[0], reverse=True)#sort by start value
					for region in regions[ref_chrom][entry][ref_chrom]:
						fasta_header = '>{} {}-{}|len={}bp|'.format(ref_chrom, region[0], region[1], region[1]-region[0]+1)
						if region[2]:
							fasta.write(fasta_header + '+\n' + pancake.seq(ref_chrom, region[0], region[1])+'\n')
						else:
							fasta.write(fasta_header + '-\n' + rev_comp(pancake.seq(ref_chrom, region[0], region[1])) +'\n')
				#write subsequences of other chroms
				for chrom in other_chroms:
					if chrom in regions[ref_chrom][entry]:
						regions[ref_chrom][entry][chrom].sort(key=lambda item: item[0], reverse=True)#sort by start value for one chromosome
						for region in regions[ref_chrom][entry][chrom]:
							fasta_header = '>{} {}-{}|len={}bp|'.format(chrom, region[0], region[1], region[1]-region[0]+1)
							if region[2]:
								fasta.write(fasta_header+'+\n')
								fasta.write(pancake.seq(chrom, region[0], region[1]))
							else:
								fasta.write(fasta_header + '-\n')
								fasta.write(rev_comp(pancake.seq(chrom, region[0], region[1])))
							fasta.write('\n')

