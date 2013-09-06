import sys
from pancake.alignment import Alignment
from pancake.utils import rev_comp
from pancake.pangenome import PanGenome


def parse_alis(f, pangenome, min_length, self_alignments=True):
	line_ind = 0
	with open(f, 'rt') as ali_file:
		for line in ali_file:
			if line[:6] == 'NUCMER':
				try:
					pangenome = parse_DELTA(f, pangenome, min_length, self_alignments)
				except:
					sys.stderr.write('ERROR while parsing {} ...SKIPPING\n'.format(f))
				break
			elif line[:5] == 'BLAST':
				try:
					pangenome = parse_BLAST(f, pangenome, min_length, self_alignments)
				except:
					sys.stderr.write('ERROR while parsing {} ...SKIPPING\n'.format(f))
				break
			if line_ind > 2:
				sys.stderr.write('...can not identify file format of {} ...SKIPPING\n'.format(f))
				break
			line_ind+=1
	return pangenome


#parse nucmer output, i.e. .delta files
#every Sequence in .delta file has to be already in pangenome
#Delta = (1, -3, 4, 0)
#A = ABC.DACBDCAC$
#B = .BCCDAC.DCAC$
def parse_DELTA(delta_file, pangenome, min_length, self_alignments=True):
	ali_count = 0
	with open(delta_file, 'r') as in_file:
		sys.stderr.write('...parsing .delta file {}\n'.format(delta_file))
		genome1, genome2 = '',''
		seq1, seq2 = '',''
		qtupel, stupel = None,None
		for line in in_file:
			if line[0]=='>':
				line_list = line.rstrip().split()
				genome1 = line_list[0][1:] # get rid of '>'
				genome2 = line_list[1]
			elif line[0] == '0': 
				if qtupel and stupel:
					#end of a pairwise alignment --> convert to Alignment Object
					ali = ( ali1 + seq1[ind1:].upper() , ali2 + seq2[ind2:].upper() ) # get gapped sequences
					ali_count+=1
					if (ali_count)%1000==0:
						pangenome.refine_unlabeled()
						pangenome.refine_adjacent_sfs()
						sys.stderr.write('...adding alignment {} ({} SFs created)\n'.format(ali_count, len(pangenome.features)))
					ali = Alignment(genome1, genome2, qtupel, stupel, ali)
					if ali.qname == ali.sname:
						#check self overlaps
						if ali.qstop > ali.sstart and ali.qstop < ali.sstop:
							#TODO
							ali_str = str(ali).split()[:2]
							sys.stderr.write('...excluding alignment\n\t{}\n\t{}\n'.format(ali_str[0], ali_str[1]))
							ali_count-=1
						elif ali.sstart > ali.qstart and ali.sstart< ali.qstop:
							#TODO
							ali_str = str(ali).split()[:2]
							sys.stderr.write('...excluding alignment\n\t{}\n\t{}\n'.format(ali_str[0], ali_str[1]))
							ali_count-=1
						else: pangenome.add_alignment(ali)
					else: pangenome.add_alignment(ali)
					qtupel, stupel = None, None
			elif genome1: #checking for genome1 makes sure not to parse header
				line_list = line.split(' ')
				if len(line_list)>1:
					if self_alignments or genome1 != genome2:
						if (genome1 != genome2 or line_list[0] != line_list[2] or line_list[1] != line_list[3]): #avoid whole genome alignment against itself
							#tuples
							qtupel = (int(line_list[0]), int(line_list[1]))
							stupel = (int(line_list[2]), int(line_list[3]))
							if qtupel[1]-qtupel[0]+1 >= min_length and max(stupel[1],stupel[0])-min(stupel[1],stupel[0])+1 >= min_length :
								ali1, ali2 = '', ''
								chrom1 = pangenome.chrom_names[genome1]
								chrom2 = pangenome.chrom_names[genome2]
								seq1 = pangenome.seq(chrom1, qtupel[0], qtupel[1]).upper() if qtupel[0]<qtupel[1] else rev_comp(pangenome.seq(chrom1, qtupel[1], qtupel[0])).upper()
								seq2 = pangenome.seq(chrom2, stupel[0], stupel[1]).upper() if stupel[0]<stupel[1] else rev_comp(pangenome.seq(chrom2, stupel[1], stupel[0])).upper()
								ind1, ind2 = 0, 0
							else: qtupel, stupel = None, None
				elif qtupel:
					#alignment modification
					if line[0] == '-':
						#deletion
						l = int(line[1:].rstrip())-1
						ali1 += seq1[ind1:ind1+l].upper() + '-'
						ali2 += seq2[ind2:ind2+l+1].upper()
						ind1 += l
						ind2 += l+1
						
					elif line[0] != '\n' and line[0] != '0':
						#insertion
						l=int(line.rstrip())-1
						ali1 +=seq1[ind1:ind1+l+1].upper()
						ali2 += seq2[ind2:ind2+l].upper() + '-'
						ind1 += l+1
						ind2 += l
	sys.stderr.write('...found {} valid pairwise alignments\n'.format(ali_count))
	return pangenome


def parse_BLAST(blast_file, pangenome, min_ali_length, self_alignments=True):
	''' parse a blastfile and return a customized data structure
	(q)uery - and (s)ubject keys : start, stop, seq'''
	new_dict = {} #stores current alignment
	new_dict['q'] = {"start" : [] , "stop" : [], "seq" : [] }
	new_dict['s'] = {"start" : [] , "stop" : [], "seq" : [] }
	with open(blast_file) as in_file:
		sys.stderr.write('...parsing BLAST file {}\n'.format(blast_file))
		ali_ind = 0 # if set: alignment line, gives first alignment index
		sbjct = ''
		for line in in_file:
			if line[:7] == 'Query= ': 
				query = line.split()[1]
			if line[0] == '>':
				if new_dict['q']['start'] and sbjct and (self_alignments or query!=sbjct):
					q_pos_tuple = (new_dict['q']['start'][0],new_dict['q']["stop"][-1] )
					s_pos_tuple = (new_dict['s']['start'][0], new_dict['s']['stop'][-1])
					if max(q_pos_tuple) - min(q_pos_tuple) +1 >= min_ali_length and max(s_pos_tuple) - min(s_pos_tuple) +1 >= min_ali_length:
						if query != sbjct or (min(q_pos_tuple), max(q_pos_tuple)) != (min(s_pos_tuple), max(s_pos_tuple)):
							ali_ind +=1
							if (ali_ind+1)%1000==0:
								pangenome.refine_unlabeled()
								pangenome.refine_adjacent_sfs()
								sys.stderr.write('...adding alignment {} ({} SFs created)\n'.format(ali_count, len(pangenome.features)))
							ali = Alignment(query, sbjct, q_pos_tuple, s_pos_tuple, (''.join(new_dict['q']['seq']), ''.join(new_dict['s']['seq'])))
							if ali.qname == ali.sname:
								#check self overlaps
								if ali.qstop > ali.sstart and ali.qstop < ali.sstop:
									#TODO
									ali_str = str(ali).split()[:2]
									sys.stderr.write('...excluding alignment\n\t{}\n\t{}\n'.format(ali_str[0], ali_str[1]))
									ali_count-=1
								elif ali.sstart > ali.qstart and ali.sstart< ali.qstop:
									#TODO
									ali_str = str(ali).split()[:2]
									sys.stderr.write('...excluding alignment\n\t{}\n\t{}\n'.format(ali_str[0], ali_str[1]))
									ali_count-=1
								else: pangenome.add_alignment(ali)
							else: pangenome.add_alignment(ali)
					new_dict['q'] = {"start" : [] , "stop" : [], "seq" : [] }
					new_dict['s'] = {"start" : [] , "stop" : [], "seq" : [] }
				sbjct = line.split()[0][1:] if line[1] != ' ' else line.split()[1]
			line_list = line.split()
			if line_list and line_list[0]=='Score' and 'Expect' in line_list:
				if new_dict['q']['start'] and (self_alignments or query!=sbjct): 
					q_pos_tuple = (new_dict["q"]["start"][0],new_dict["q"]["stop"][-1] )
					s_pos_tuple = (new_dict["s"]["start"][0], new_dict["s"]["stop"][-1])
					if max(q_pos_tuple) - min(q_pos_tuple) +1 >= min_ali_length and max(s_pos_tuple) - min(s_pos_tuple) +1 >= min_ali_length:
						if query != sbjct or self_alignments:
							if (min(q_pos_tuple), max(q_pos_tuple)) != (min(s_pos_tuple), max(s_pos_tuple)):
								ali_ind +=1
								if (ali_ind+1)%1000==0:
									sys.stderr.write('...adding alignment {} ({} SFs created)\n'.format(ali_count, len(pangenome.features)))
								ali = Alignment(query, sbjct, q_pos_tuple, s_pos_tuple, (''.join(new_dict["q"]["seq"]), ''.join(new_dict["s"]["seq"])))
								if ali.qname == ali.sname:
								#check self overlaps
									if ali.qstop > ali.sstart and ali.qstop < ali.sstop:
										#TODO
										ali_str = str(ali).split()[:2]
										sys.stderr.write('...excluding alignment\n\t{}\n\t{}\n'.format(ali_str[0], ali_str[1]))
										ali_count-=1
									elif ali.sstart > ali.qstart and ali.sstart< ali.qstop:
										#TODO
										ali_str = str(ali).split()[:2]
										sys.stderr.write('...excluding alignment\n\t{}\n\t{}\n'.format(ali_str[0], ali_str[1]))
										ali_count-=1
									else: pangenome.add_alignment(ali)
								else: pangenome.add_alignment(ali)
				new_dict['q'] = {"start" : [] , "stop" : [], "seq" : [] }
				new_dict['s'] = {"start" : [] , "stop" : [], "seq" : [] }
			if sbjct and line[:5] == 'Query':
				new_dict['q']['start'].append(int(line_list[1]))
				new_dict["q"]["seq"].append(line_list[-2])
				new_dict["q"]["stop"].append(int(line_list[-1]))
			if line[:5] == 'Sbjct':
				new_dict["s"]["start"].append(int(line_list[1]))
				new_dict["s"]["seq"].append(line_list[-2])
				new_dict["s"]["stop"].append(int(line_list[-1]))
	if new_dict['q']['start'] and (self_alignments or query!=sbjct): 
		q_pos_tuple = (new_dict["q"]["start"][0],new_dict["q"]["stop"][-1] )
		s_pos_tuple = (new_dict["s"]["start"][0], new_dict["s"]["stop"][-1])
		if max(q_pos_tuple) - min(q_pos_tuple) +1 >= min_ali_length and max(s_pos_tuple) - min(s_pos_tuple) +1 >= min_ali_length:
			if query != sbjct or q_pos_tuple != s_pos_tuple:
				ali_ind+=1
				ali = Alignment(query, sbjct, q_pos_tuple, s_pos_tuple, (''.join(new_dict["q"]["seq"]), ''.join(new_dict["s"]["seq"])))
				pangenome.add_alignment(ali)
	sys.stderr.write('...found {} valid pairwise alignments\n'.format(ali_ind))
	return pangenome


if __name__ == "__main__":
	pass

