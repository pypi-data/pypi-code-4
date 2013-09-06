import sys
from pancake.fi import FeatureInstance
from pancake.sf import SharedFeature
from pancake.chromosome import Chromosome
from pancake.editops import EditOps,editops_from_ali
from pancake.utils import rev_comp,needle_wunsch,turn_ops,ali_refinement,new_ops_from_ops,ops_from_ops_and_ali


pos_interval = 10000

class PanGenome:

	def __init__(self):
		self.features = set() #set of Shared Features, holds all labeled FI or part of an alignment
		self.unlabeled = {} # foreach chromosome: SET of unlabeled FIs  
		self.chromosome_stops = {} # foreach chromosome (key): stop FI
		self.chrom_names = {} # foreach chromosome_name (key): a Chromosome
		self.genomes = {} #foreach genome: SET of chromosomes
		self.chromosomes = {} #foreach chromosome: a dictionary of start positions

	def __str__(self):
		out = ''
		for chrom in self.chromosomes:
			out += str(chrom) + '\n' + len(str(chrom)) * '-' + '\n'
			unlabeled_list = list(self.unlabeled[chrom])
			unlabeled_list.sort(key=lambda x: x.start)
			for fi in unlabeled_list.sort:
				out += str(fi) + '\n'
			out += '#\n'
		out += '#-#-#\n\n'
		for sf in self.features:
			out+= str(sf) +'\n'
		return out

	def add_chromosome(self, name, seq, genome=None):
		if not genome: genome=name
		chrom = Chromosome(name, genome)
		if genome not in self.genomes: self.genomes[genome] = set()
		self.genomes[genome].add(chrom)
		self.chrom_names[name] = chrom
		fi = FeatureInstance( chrom, 1, len(seq), seq.upper(), None, None, None )
		self.chromosome_stops[chrom] = fi
		self.unlabeled[chrom] = set([fi])
		self.chromosomes[chrom] = {}
		for pos_ind in range(int(self.chrom_length(chrom)/pos_interval) +1):
			self.chromosomes[chrom][pos_ind * pos_interval +1] = fi

	def add_alignment(self, ali):
		while ali: 
			#sys.stderr.write(self.seq(self.chrom_names['gi|372116212|gb|CP003216.1|'], 2178033, 2178035) +'\n')
			ali = self.add_ali(ali)
		return self

	def add_ali(self, ali):
		qchrom = self.chrom_names[ali.qname]
		schrom = self.chrom_names[ali.sname]
		if ali.qstop-ali.qstart > -1 and ali.sstop-ali.sstart > -1:
			q_init_fi, q_overlap, s_init_fi, s_overlap = self.start_parameters(ali)
		
			#treat initial q_fi (at ali begin)
			if self.treat_init_fi_at_ali_begin(ali.qstrand, q_init_fi, q_overlap): 
				q_init_fi, q_overlap, s_init_fi, s_overlap = self.start_parameters(ali)
			#treat initial s_fi (at ali begin)
			if self.treat_init_fi_at_ali_begin(ali.sstrand, s_init_fi, s_overlap): 
				q_init_fi, q_overlap, s_init_fi, s_overlap = self.start_parameters(ali)

			#check alignmnets at alignment end
			if self.treat_init_fi_at_ali_end(ali.qstrand, q_init_fi, q_overlap): 
				q_init_fi, q_overlap, s_init_fi, s_overlap = self.start_parameters(ali)
			if self.treat_init_fi_at_ali_end(ali.sstrand, s_init_fi, s_overlap): 
				q_init_fi, q_overlap, s_init_fi, s_overlap = self.start_parameters(ali)

			qcut, scut = 0, 0
			if ali.qstrand and q_overlap[1] > 0: qcut = q_overlap[1]
			if not ali.qstrand and q_overlap[0] > 0: qcut = q_overlap[0]

			if ali.sstrand and s_overlap[1] > 0: scut =s_overlap[1]
			if not ali.sstrand and s_overlap[0] > 0: scut = s_overlap[0]
			#print('qcut', qcut, 'scut', scut)
			if qcut == 0:
				if scut == 0:
					if not q_init_fi.sh_feat or not s_init_fi.sh_feat or q_init_fi.sh_feat != s_init_fi.sh_feat:
						self.merge_sfs(ali, q_init_fi, s_init_fi)
				else:
					#scut>0: find cut_index in alignment
					#always from alignment start, marks #bases in first alignment part
					ali_stop_ind = s_init_fi.stop - s_init_fi.start+1
					ali1, ali2 = ali.divide(ali_stop_ind, False)

					#cut q_init_fi
					if ali1: # and ali1.sstop -ali1.sstart > -1 and ali1.qstop -ali1.qstart > -1:
						self.add_ali(ali1)

					if ali2:
						return ali2 #self.add_alignment(ali2)
					
			else:
				#qcut>0
				if scut == 0:
					ali_stop_ind = q_init_fi.stop - q_init_fi.start+1
					ali1, ali2 = ali.divide(ali_stop_ind, True)
					if ali1:
						self.add_ali(ali1)
					if ali2:
						return ali2 #self.add_alignment(ali2)

				else:
					#qcut>0 and scut>0
					#find cut_ind
					q_stop_ind = q_init_fi.stop - q_init_fi.start + 1
					s_stop_ind = s_init_fi.stop -s_init_fi.start + 1

					i, c1, c2 = 0, 0, 0
					while (c1 < q_stop_ind and c2 < s_stop_ind):
						c1 += ali.qali[i] != '-'
						c2 += ali.sali[i] != '-'
						i += 1
					cut1 = len(ali.qali[:i].replace('-', ''))
					cut2 = len(ali.sali[:i].replace('-', ''))

					if cut1 >0:
						ali1, ali2 = ali.divide(cut1, True)
					elif cut2>0:
						ali1, ali2 = ali.divide(cut2, False)
					else: ali1, ali2 = None, None 

					while ali1:
						ali1 = self.add_ali(ali1)

					if ali2:
						return ali2
		else: return None


	#cut initial fis at alignment begin, strand = ali.strand
	def treat_init_fi_at_ali_begin(self, strand, fi, overlaps):
		treated=False
		fi_strand = not fi.seq.reverse if fi.sh_feat else True
		if strand:
			if overlaps[0] <0:
				if fi_strand:
					self.treat_start(fi, abs(overlaps[0]))
				else:
					self.treat_stop(fi, abs(overlaps[0]))
				treated =True
		else:
			#start_fi is stop_fi!
			if overlaps[1] < 0:
				if fi_strand:
					self.treat_stop(fi, abs(overlaps[1]))
				else:
					self.treat_start(fi, abs(overlaps[1]))
				treated = True
		return treated

	#cut initial fis at alignment end
	def treat_init_fi_at_ali_end(self, strand, fi, overlaps):
		treated=False
		fi_strand = not fi.seq.reverse if fi.sh_feat else True
		if strand:
			if overlaps[1] <0:
				if fi_strand:
					self.treat_stop(fi, abs(overlaps[1]))
				else:
					self.treat_start(fi, abs(overlaps[1]))
				treated =True
		else:
			if overlaps[0] < 0:
				if fi_strand:
					self.treat_start(fi, abs(overlaps[0]))
				else:
					self.treat_stop(fi, abs(overlaps[0]))
				treated = True
		return treated


	# ACGTAG, overlap=2 --> AC|GTAG
	def treat_start(self, ref_fi, overlap):
		if ref_fi.sh_feat:
			fi1, fi2 = self.treat_labeled_overlap( ref_fi, overlap)
		else:
			fi1, fi2 = self.treat_unlabeled_overlap(ref_fi, overlap)
		return fi1, fi2


	def treat_labeled_overlap(self, ref_fi, overlap):

		#make sure that ref_fi is in + direction
		if ref_fi.seq.reverse: 
			ref_fi.sh_feat.turn()
			overlap = ref_fi.stop-ref_fi.start - overlap +1
		#cut_ind = ref_fi.seq.ref_cut_ind(overlap) # cutting index of reference sequence in shared feature index: should not be applied for ref_fi!
		cut_ind, ref_ops1,ref_ops2 = ref_fi.seq.ref_cut_ind_and_ref_ops(overlap)
		sf = ref_fi.sh_feat
		new_sf1 = SharedFeature(sf.seq[:cut_ind])
		new_sf2 = SharedFeature(sf.seq[cut_ind:])
		return_fi1, return_fi2 = None, None
		for fi in list(sf):
			#reference feature instance is forward
			new_edit_ops = fi.seq.divide(cut_ind) if fi!=ref_fi else (ref_ops1,ref_ops2)
			l1 = len(new_edit_ops[0])
			l2 = len(new_edit_ops[1])
			if l1 >0 and l2 >0:
				if not fi.seq.reverse:
					new_fi1 = FeatureInstance(fi.chrom, fi.start, fi.start+l1-1, new_edit_ops[0], new_sf1, None, fi.prevFI)
					new_sf1.add(new_fi1)

					new_fi2 = FeatureInstance(fi.chrom, fi.start+l1, fi.stop , new_edit_ops[1], new_sf2, fi.nextFI, new_fi1)
					new_sf2.add(new_fi2)
					
					new_fi1.nextFI = new_fi2
					
					if new_fi1.prevFI:
						new_fi1.prevFI.nextFI = new_fi1
					if new_fi2.nextFI:
						new_fi2.nextFI.prevFI = new_fi2
					else:
						self.chromosome_stops[new_fi2.chrom] = new_fi2
				#reverse fi
				else:
					new_fi1 = FeatureInstance(fi.chrom, fi.stop-l1+1, fi.stop, new_edit_ops[0], new_sf1, fi.nextFI, None)
					new_sf1.add(new_fi1)
					new_fi2 = FeatureInstance(fi.chrom, fi.start, fi.stop-l1, new_edit_ops[1],new_sf2, new_fi1, fi.prevFI )
					new_sf2.add(new_fi2)
				
					new_fi1.prevFI = new_fi2
					if fi.prevFI:
						fi.prevFI.nextFI = new_fi2
					if fi.nextFI:
						fi.nextFI.prevFI = new_fi1
					else:
						self.chromosome_stops[fi.chrom] = new_fi1
				if fi==ref_fi: return_fi1, return_fi2 = new_fi1, new_fi2
				#update self.chromosomes
				start, stop = new_fi1.start, new_fi1.stop
				iter_start = (start//pos_interval)+1 if start>(start//pos_interval) * pos_interval+1 else start//pos_interval
				iter_stop = stop//pos_interval+1 if stop >= (stop//pos_interval) * pos_interval+1 else stop//pos_interval
				for pos in [i*pos_interval +1 for i in range(iter_start, iter_stop)]:
					self.chromosomes[new_fi1.chrom][pos] = new_fi1
				start, stop = new_fi2.start, new_fi2.stop
				iter_start = (start//pos_interval)+1 if start>(start//pos_interval) * pos_interval+1 else start//pos_interval
				iter_stop = stop//pos_interval+1 if stop >= (stop//pos_interval) * pos_interval+1 else stop//pos_interval
				for pos in [i*pos_interval +1 for i in range(iter_start, iter_stop)]:
					self.chromosomes[new_fi2.chrom][pos] = new_fi2

			elif l1 > 0:
				#print('l1>0')
				fi.seq = new_edit_ops[0]
				fi.sh_feat = new_sf1
				new_sf1.add(fi)
				if fi==ref_fi: return_fi1 = fi
			elif l2 > 0:
				#print('l2>0')
				fi.seq = new_edit_ops[1]
				fi.sh_feat = new_sf2
				new_sf2.add(fi)
				if fi==ref_fi: return_fi2 = fi
			else:
				break
		if new_sf1 and len(new_sf1.seq) == 0:
			new_sf1.treat_empty_seq()
		if new_sf2 and len(new_sf2.seq) == 0:
			new_sf2.treat_empty_seq()
		self.features.add(new_sf1)
		self.features.add(new_sf2)
		try:
			self.features.remove(sf)
		except:
			sys.stderr.write('Tried to remove\n{}\n{}\n{}\n{}\n'.format(sf, ref_fi.sh_feat, return_fi1.sh_feat, return_fi2.sh_feat))
		#TODO check if necessary
		#self.check_non_similarity(new_sf1)
		#self.check_non_similarity(new_sf2)
		return return_fi1, return_fi2

	def treat_unlabeled_overlap(self, ref_fi, overlap):
			#unlabeled --> unlabeled (ref_fi, l=overlap) + unlabeled (new_fi)
			ref_chrom = ref_fi.chrom
			self.unlabeled[ref_chrom].remove(ref_fi)
			new_fi = FeatureInstance(ref_chrom, ref_fi.start+abs(overlap), ref_fi.stop, ref_fi.seq[overlap:], None, ref_fi.nextFI, ref_fi)
			if new_fi.nextFI:
				new_fi.nextFI.prevFI = new_fi
			else:
				self.chromosome_stops[ref_chrom] = new_fi
			ref_fi.stop = new_fi.start-1
			ref_fi.seq = ref_fi.seq[:overlap]
			ref_fi.nextFI = new_fi
			if ref_fi.prevFI:
				ref_fi.prevFI.nextFI = ref_fi

			self.unlabeled[ref_chrom].add(ref_fi)
			self.unlabeled[ref_chrom].add(new_fi)
			
			start, stop = ref_fi.start, ref_fi.stop
			iter_start = (start//pos_interval)+1 if start>(start//pos_interval) * pos_interval+1 else start//pos_interval
			iter_stop = stop//pos_interval+1 if stop >= (stop//pos_interval) * pos_interval+1 else stop//pos_interval
			for pos in [i*pos_interval +1 for i in range(iter_start, iter_stop)]:
				self.chromosomes[ref_chrom][pos] = ref_fi
			start, stop = new_fi.start, new_fi.stop
			iter_start = (start//pos_interval)+1 if start>(start//pos_interval) * pos_interval+1 else start//pos_interval
			iter_stop = stop//pos_interval+1 if stop >= (stop//pos_interval) * pos_interval+1 else stop//pos_interval
			for pos in [i*pos_interval +1 for i in range(iter_start, iter_stop)]:
				self.chromosomes[ref_chrom][pos] = new_fi
			return ref_fi, new_fi

	# ACGTAG, overlap=2 --> ACGT|AG
	def treat_stop(self, ref_fi, overlap):
		#treat stop is nothing else than treat_start with adapted parameters
		if ref_fi.sh_feat:
			fi1, fi2 = self.treat_labeled_overlap(ref_fi, ref_fi.stop-overlap-ref_fi.start+1)
		else:
			fi1, fi2 = self.treat_unlabeled_overlap(ref_fi, ref_fi.stop-overlap-ref_fi.start+1)
		return fi1, fi2

	def start_parameters(self, ali):
		#overlap[0] always concerns start parameters, overlap[1] always concerns stop parameters, regardless of strand
		#query
		if ali.qstrand:
			q_fi =  self.crossing_fi(self.chrom_names[ali.qname], ali.qstart)
		else:
			q_fi =  self.crossing_fi(self.chrom_names[ali.qname], ali.qstop)
		q_overlap = (q_fi.start-ali.qstart, ali.qstop - q_fi.stop)
		#subject
		if ali.sstrand:
			s_fi = self.crossing_fi(self.chrom_names[ali.sname], ali.sstart)
		else:
			s_fi = self.crossing_fi(self.chrom_names[ali.sname], ali.sstop)
		s_overlap = (s_fi.start-ali.sstart, ali.sstop - s_fi.stop)
		return (q_fi, q_overlap, s_fi, s_overlap)

	def crossing_fi(self, chrom, pos):
		index = (pos-1) // pos_interval * pos_interval +1
		if pos -index < index + pos_interval -pos or index+pos_interval not in self.chromosomes[chrom]:
			start_fi = self.chromosomes[chrom][index]
			while(start_fi.stop < pos) and start_fi.nextFI:
				start_fi = start_fi.nextFI
		else:
			start_fi = self.chromosomes[chrom][index+pos_interval]
			while(start_fi.start > pos) and start_fi.prevFI:
				start_fi = start_fi.prevFI
		return start_fi

	def chrom_length(self, chrom):
		return self.chromosome_stops[chrom].stop

	def seq(self, chrom, start=1, stop=None, start_fi =None):
		#catch ERROR indices and ERROR genome
		if not stop: stop = self.chrom_length(chrom)
		if stop > self.chrom_length(chrom): 
			sys.stderr.write('While Sequence Retrieval: Stop position {} not in {}. Set to chromosome length = {}.\n'.format(stop, chrom, self.chrom_length(chrom)))
		#get start_fi
		if not start_fi: 
			start_fi = self.crossing_fi(chrom, start)
		begin_olp = start_fi.start-start
		seq_list = []
		seq_list.append(start_fi.sequence()[abs(begin_olp):])
		end_olp = stop-start_fi.stop
		if end_olp<0:
			seq_list[0] = seq_list[0][:end_olp]
		elif end_olp>0:
			while start_fi.stop < stop:
				start_fi = start_fi.nextFI
				seq_list.append(start_fi.sequence())
				if start_fi.stop > stop:
					seq_list[-1] = seq_list[-1][:-(start_fi.stop-stop)]
		return ''.join(seq_list)


	def merge_sfs(self, ali, q_start_fi, s_start_fi):
		#FI/SF handling
		if not q_start_fi.sh_feat:
			q_start_fi = self.convert_to_sf(q_start_fi)
		if not s_start_fi.sh_feat:
			s_start_fi = self.convert_to_sf(s_start_fi)

		if len(s_start_fi.sh_feat) > len(q_start_fi.sh_feat):
			ali.convert()
			q_start_fi, s_start_fi = s_start_fi, q_start_fi

		qsf = q_start_fi.sh_feat #this will get more entries
		old_sf = s_start_fi.sh_feat # this will be deleted

		if ali.qstrand and q_start_fi.seq.reverse: qsf.turn()
		elif not ali.qstrand and not q_start_fi.seq.reverse: qsf.turn()
		q_ref_ali = q_start_fi.seq.get_alignment(qsf.seq) #alignment of qsf.seq and q_start_fi.seq

		#ali.sali and s_start_fi are in same direction
		if ali.sstrand and s_start_fi.seq.reverse: old_sf.turn()
		elif not ali.sstrand and not s_start_fi.seq.reverse: old_sf.turn()


		#qali is always in right direction
		qsf_seq_ops = ops_from_ops_and_ali(list(q_start_fi.seq.ops), qsf.seq, ali.qali, ali.sali) #ops of ali.sali rebased to qsf.seq
		qsf_seq_ops = ali_refinement(qsf.seq, qsf_seq_ops)

		sseq = ali.sali.replace('-','')
		turned_ops = turn_ops(qsf.seq, list(qsf_seq_ops)) # get editops for qsf.seq based on s_start_fi.seq
		if len(old_sf) >1:
			ali_dic = old_sf.alignments_to_entry(s_start_fi) #alignment of s_start_fi.seq and entry
			for entry in ali_dic:
				other_ops = new_ops_from_ops(list(turned_ops), ali_dic[entry], sseq)
				other_ops = ali_refinement(qsf.seq, other_ops)
				entry.sh_feat = qsf
				entry.seq.ops = other_ops
				qsf.add(entry)
				if entry.nextFI:
					entry.nextFI.prevFI = entry
				else: 
					self.chromosome_stops[entry.chrom] = entry
				if entry.prevFI:
					entry.prevFI.nextFI = entry
				#update pancake.chromosomes
				start, stop = entry.start, entry.stop
				iter_start = (start//pos_interval)+1 if start>(start//pos_interval) * pos_interval+1 else start//pos_interval
				iter_stop = stop//pos_interval+1 if stop >= (stop//pos_interval) * pos_interval+1 else stop//pos_interval
				for pos in [i*pos_interval +1 for i in range(iter_start, iter_stop)]:
					self.chromosomes[entry.chrom][pos] = entry
		s_start_fi.sh_feat = qsf
		qsf.add(s_start_fi)
		s_start_fi.seq.ops = qsf_seq_ops
		if s_start_fi.nextFI: 
			s_start_fi.nextFI.prevFI = s_start_fi
		else:
			self.chromosome_stops[s_start_fi.chrom] = s_start_fi
		if s_start_fi.prevFI:
			s_start_fi.prevFI.nextFI = s_start_fi
		#index update
		start, stop = s_start_fi.start, s_start_fi.stop
		iter_start = (start//pos_interval)+1 if start>(start//pos_interval) * pos_interval+1 else start//pos_interval
		iter_stop = stop//pos_interval+1 if stop >= (stop//pos_interval) * pos_interval+1 else stop//pos_interval
		for pos in [i*pos_interval +1 for i in range(iter_start, iter_stop)]:
			self.chromosomes[s_start_fi.chrom][pos] = s_start_fi
		self.features.remove(old_sf)


	def convert_to_sf(self, fi):
		#convert unlabeled fi into shared feature
		self.unlabeled[fi.chrom].remove(fi)
		new_sf = SharedFeature(fi.seq.upper(), {fi})
		fi.seq = EditOps([fi.stop-fi.start+1])
		
		fi.sh_feat = new_sf
		if fi.nextFI: 
			fi.nextFI.prevFI = fi
		else:
			self.chromosome_stops[fi.chrom] = fi
		if fi.prevFI:
			fi.prevFI.nextFI = fi
		#update pancake.chromosomes
		start, stop = fi.start, fi.stop
		iter_start = (start//pos_interval)+1 if start>(start//pos_interval) * pos_interval+1 else start//pos_interval
		iter_stop = stop//pos_interval+1 if stop >= (stop//pos_interval) * pos_interval+1 else stop//pos_interval
		for pos in [i*pos_interval +1 for i in range(iter_start, iter_stop)]:
			self.chromosomes[fi.chrom][pos] = fi
		self.features.add(new_sf)
		return fi


###PanCake Refinement

	def refine_adjacent_sfs(self):
	
		#check unlabeled
		for chrom in self.unlabeled:
			concatenation = True
			while concatenation:
				entry_list = list(self.unlabeled[chrom])
				concatenation =False
				for entry in entry_list:
					if entry.nextFI in entry_list:
						self.unlabeled[chrom].remove(entry.nextFI)
						entry.seq += entry.nextFI.seq
						entry.stop = entry.nextFI.stop
						entry.nextFI = entry.nextFI.nextFI
						if entry.nextFI:
							entry.nextFI.prevFI = entry
						else:
							self.chromosome_stops[chrom] = entry
						if entry.prevFI: entry.prevFI.nextFI = entry
						#index update
						start, stop = entry.start, entry.stop
						iter_start = (start//pos_interval)+1 if start>(start//pos_interval) * pos_interval+1 else start//pos_interval
						iter_stop = stop//pos_interval+1 if stop >= (stop//pos_interval) * pos_interval+1 else stop//pos_interval
						for pos in [i*pos_interval +1 for i in range(iter_start, iter_stop)]:
							self.chromosomes[chrom][pos] = entry
						concatenation = True
						break
	
		'''join CSOs with perfectly adjacent entries'''
		#check sfs
		sf_list = list(self.features)
		while sf_list:
			sf = sf_list[0]
			sec_sf = None
			entry_list = list(sf.entries)
			start_entry, entry_list = entry_list[0], entry_list[1:]
			ok_flag = True
			if start_entry.seq.reverse: start_entry.sh_feat.turn()

			#check forward (nextFI.sh_feat)
			ref_fi = start_entry.nextFI
			if ref_fi and ref_fi.sh_feat:
				if ref_fi.seq.reverse: ref_fi.sh_feat.turn()
				next_sf = ref_fi.sh_feat
			else:
				ok_flag = False
			if ok_flag and next_sf and len(sf) == len(next_sf):
				for fi in entry_list:
					if not ok_flag: break
					if not fi.seq.reverse:
						next_fi = fi.nextFI
						if not next_fi or not next_fi.sh_feat: ok_flag = False
						elif next_fi.sh_feat and (next_fi.sh_feat != next_sf or next_fi.seq.reverse != fi.seq.reverse): ok_flag = False
					else:
						prev_fi = fi.prevFI
						if not prev_fi or not prev_fi.sh_feat: ok_flag=False
						elif prev_fi.sh_feat and (prev_fi.sh_feat != next_sf or prev_fi.seq.reverse != fi.seq.reverse): ok_flag = False
			else: ok_flag = False

			#if ok_flag: concatenate, update list
			if ok_flag:
				self.concatenate_sfs(sf, next_sf)
				if next_sf in sf_list: sf_list.remove(next_sf)
			else:
				#check backward
				ok_flag=True
				ref_fi = start_entry.prevFI
				if ref_fi and ref_fi.sh_feat:
					if ref_fi.seq.reverse : ref_fi.sh_feat.turn()
					prev_sf = ref_fi.sh_feat
				else: ok_flag = False
				
				if ok_flag and prev_sf and len(sf) == len(prev_sf):
					for fi in entry_list:
						if not fi.seq.reverse:
							prev_fi = fi.prevFI
							if not prev_fi or not prev_fi.sh_feat: ok_flag = False
							elif prev_fi.sh_feat and (prev_fi.sh_feat != prev_sf or prev_fi.seq.reverse != fi.seq.reverse): ok_flag = False
						else:
							next_fi = fi.nextFI
							if not next_fi or not next_fi.sh_feat: ok_flag=False
							elif next_fi.sh_feat and (next_fi.sh_feat != prev_sf or next_fi.seq.reverse != fi.seq.reverse): ok_flag = False
				else: ok_flag=False

				if ok_flag:
					self.concatenate_sfs(prev_sf, sf)
					if sf in sf_list: sf_list.remove(sf)
				else:
					#not adjacent, remove from list
					sf_list.remove(sf)


	def concatenate_sfs(self, sf, sec_sf):
		#check SFs
		entry_list = list(sf.entries)
		sf.seq = sf.seq + sec_sf.seq
		for fi in entry_list:
			if not fi.seq.reverse:
				fi2 = fi.nextFI
				fol_sf = fi2.sh_feat if fi2 else None
			else:
				fi2 = fi.prevFI
				fol_sf = fi2.sh_feat if fi2 else None
			if fol_sf != sec_sf:
				raise ValueError('This went wrong')
			if type(fi.seq.ops[-1]) == int and type(fi2.seq.ops[0])==int:
				if (fi.seq.ops[-1] > 0 and fi2.seq.ops[0] > 0) or (fi.seq.ops[-1] < 0 and fi2.seq.ops[0] < 0):
					new_edit_ops = EditOps(fi.seq.ops[:-1] + [fi.seq.ops[-1] + fi2.seq.ops[0]] + fi2.seq.ops[1:])
				else:
					new_edit_ops = EditOps(fi.seq.ops + fi2.seq.ops)
			else:
				new_edit_ops = EditOps(fi.seq.ops + fi2.seq.ops)
			if fi2.seq.reverse: new_edit_ops.reverse = True

			fi.seq = new_edit_ops
			if not fi.seq.reverse:
				next_fi = fi2.nextFI
				prev_fi = fi.prevFI
				fi.stop = fi2.stop
			else:
				next_fi = fi.nextFI
				prev_fi = fi2.prevFI
				fi.start = fi2.start
			fi.nextFI = next_fi
			fi.prevFI = prev_fi

			if prev_fi: 
				prev_fi.nextFI = fi
			if next_fi:
				next_fi.prevFI = fi
			else:
				self.chromosome_stops[fi.chrom] = fi
			
			start, stop = fi.start, fi.stop
			iter_start = (start//pos_interval)+1 if start>(start//pos_interval) * pos_interval+1 else start//pos_interval
			iter_stop = stop//pos_interval+1 if stop >= (stop//pos_interval) * pos_interval+1 else stop//pos_interval
			for pos in [i*pos_interval +1 for i in range(iter_start, iter_stop)]:
				self.chromosomes[fi.chrom][pos] = fi

		self.features.remove(sec_sf)
		for fi in sec_sf:
			del (fi)
		del (sec_sf)


	def refine_unlabeled(self):
		#identifies Shared Features with only 1 entry and integrate them in self.unlabeled
		lonley_sfs=[]
		for sf in self.features:
			if len(sf) ==1: lonley_sfs.append(sf)
		for sf in lonley_sfs:
			ind, ufi_ind = -1, 0
			fi = list(sf.entries)[0]
			if fi.seq.reverse: fi.sh_feat.turn() #unlabeled fis are always 'forward'
			fi.seq = fi.seq.seq(fi.sh_feat.seq)
			self.features.remove(fi.sh_feat)
			fi.sh_feat = None
			if fi.nextFI:
				fi.nextFI.prevFI = fi
			else: self.chromosome_stops[fi.chrom] = fi
			if fi.prevFI:
				fi.prevFI.nextFI = fi
			if fi.prevFI in self.unlabeled[fi.chrom]:
				#concatenate fi with previous fi
				self.unlabeled[fi.chrom].remove(fi.prevFI)
				fi.start = fi.prevFI.start
				fi.seq = fi.prevFI.seq + fi.seq
				fi.prevFI = fi.prevFI.prevFI
				if fi.prevFI:
					fi.prevFI.nextFI = fi
				if fi.nextFI:
					fi.nextFI.prevFI = fi
				else: self.chromosome_stops[fi.chrom] = fi

			if fi.nextFI in self.unlabeled[fi.chrom]:
				#concatenate fi with next fi
				self.unlabeled[fi.chrom].remove(fi.nextFI)
				fi.stop = fi.nextFI.stop
				fi.seq += fi.nextFI.seq
				fi.nextFI = fi.nextFI.nextFI
				if fi.prevFI:
					fi.prevFI.nextFI = fi
				if fi.nextFI:
					fi.nextFI.prevFI = fi
				else: self.chromosome_stops[fi.chrom] = fi

			#update self.chromosomes
			start, stop = fi.start, fi.stop
			iter_start = (start//pos_interval)+1 if start>(start//pos_interval) * pos_interval+1 else start//pos_interval
			iter_stop = stop//pos_interval+1 if stop >= (stop//pos_interval) * pos_interval+1 else stop//pos_interval
			for pos in [i*pos_interval +1 for i in range(iter_start, iter_stop)]:
				self.chromosomes[fi.chrom][pos] = fi
			
			self.unlabeled[fi.chrom].add(fi)

	def check_non_similarity(self):
		sfs=list(self.features)
		for sf in sfs:
			self.check_sf_for_non_similarity(sf)

	def check_sf_for_non_similarity(self, sf):
		tmp_fis = set([0])
		while tmp_fis:
			tmp_fis = set()
			for fi in sf.entries:
				similarity_flag = False
				for op in fi.seq.ops:
					if type(op) == int and op>0:
						similarity_flag = True
						break
				if not similarity_flag:
					#only substitutions, deletions and insertions in fi's editops
					tmp_fis.add(fi)

			if tmp_fis:
				new_sf = SharedFeature('')
				for fi in tmp_fis:
					fi.seq.ops = list(fi.seq.seq(sf.seq).upper())
					fi.sh_feat = new_sf
					sf.entries.remove(fi)
					new_sf.add(fi)
					if fi.nextFI:
						fi.nextFI.prevFI = fi
					else: self.chromosome_stops[fi.chrom] = fi
					if fi.prevFI:
						fi.prevFI.nextFI = fi
					#update self.chromosomes
					start, stop = fi.start, fi.stop
					iter_start = (start//pos_interval)+1 if start>(start//pos_interval) * pos_interval+1 else start//pos_interval
					iter_stop = stop//pos_interval+1 if stop >= (stop//pos_interval) * pos_interval+1 else stop//pos_interval
					for pos in [i*pos_interval +1 for i in range(iter_start, iter_stop)]:
						self.chromosomes[fi.chrom][pos] = fi
				new_sf.treat_empty_seq()
				if len(sf.entries) == 0:
					self.features.remove(sf)
				self.features.add(new_sf)
				sf = new_sf


######PanCake Serialization

	def compress(self, pan_file):
		'''compress into given pan_file'''
		with open(pan_file, 'wt') as out_file:
			sf_dict = {}
			i = 1
			for sf in self.features:
				sf_dict[sf] = i
				out_file.write(sf.seq + '\n')
				i+=1
			for chrom in self.chromosomes:
				out_file.write('#' + chrom.name)
				for chr_name in self.chrom_names:
					if self.chrom_names[chr_name]==chrom and chr_name != chrom.name: out_file.write(',' + chr_name)

				out_file.write(',({})'.format(chrom.genome))
				out_file.write('\n')
				fi = self.chromosomes[chrom][1]
				while fi:
					if fi.sh_feat: fi.seq.treat_double_matches() #TODO avoid this
					out_file.write(str(fi.stop) + ' ' + str(fi.seq))
					if fi.sh_feat: out_file.write(' ' + str(sf_dict[fi.sh_feat]))
					out_file.write('\n')
					fi = fi.nextFI


def decompress(pan_file):
	fi_part = False
	sf_dict={}
	sf_count = 1
	prev_fi = None
	chrom = None

	pancake = PanGenome()
	with open(pan_file, 'rt') as in_file:
		for line in in_file:
			if line[0] == '#': fi_part=True #all SFs parsed
			if not fi_part:
				sf_dict[sf_count] = SharedFeature(line[:-1])
				pancake.features.add(sf_dict[sf_count])
				sf_count+=1
			else:
				if line[0] == '#':
					chrom_names = line[1:-1].split(',')
					genome = chrom_names[-1][1:-1]
					if genome not in pancake.genomes: pancake.genomes[genome] = set()
					chrom = Chromosome(chrom_names[0], genome)
					pancake.genomes[genome].add(chrom)
					pancake.chromosome_stops[chrom] = None
					pancake.chromosomes[chrom] = {}
					pancake.unlabeled[chrom] = set()
					prev_fi = None
					for chrom_name in chrom_names[:-1]: pancake.chrom_names[chrom_name] = chrom
				else:
					line_list = line[:-1].split(' ')
					if len(line_list) == 2:
						seq = line_list[1]
						sf=None
					else:
						if line_list[1][0] == '-':
							seq = EditOps(line_list[1][1:], True)
						else:
							seq = EditOps(line_list[1], False)
						sf=sf_dict[int(line_list[2])]
						seq.list_ops()
					
					if not prev_fi:
						fi = FeatureInstance(chrom, start=1, stop=int(line_list[0]), seq = seq, sh_feat=sf, nextFI=None, prevFI=None)
						pancake.chromosomes[chrom][1] = fi
					else:
						fi = FeatureInstance(chrom, start=prev_fi.stop+1, stop=int(line_list[0]), seq = seq, sh_feat=sf, nextFI=None, prevFI=prev_fi)
						prev_fi.nextFI = fi
					pancake.chromosome_stops[chrom] = fi
					prev_fi = fi
					if fi.sh_feat != None: sf.add(fi)
					else: pancake.unlabeled[chrom].add(fi)
	#update pancake.chromosomes
	for chrom in pancake.chromosomes:
		start_fi = pancake.chromosomes[chrom][1]
		while start_fi:
			start, stop = start_fi.start, start_fi.stop
			iter_start = (start//pos_interval)+1 if start>(start//pos_interval) * pos_interval+1 else start//pos_interval
			iter_stop = stop//pos_interval+1 if stop >= (stop//pos_interval) * pos_interval+1 else stop//pos_interval
			for pos in [i*pos_interval +1 for i in range(iter_start, iter_stop)]:
				pancake.chromosomes[chrom][pos] = start_fi
			start_fi = start_fi.nextFI
	return pancake


if __name__ == "__main__":
	pass
