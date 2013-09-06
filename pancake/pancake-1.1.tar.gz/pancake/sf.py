from pancake.utils import rev_comp, get_new_alignment, new_ops_from_ops, ali_refinement
from pancake.editops import editops_from_seqs


class SharedFeature:

	def __init__(self, reference, entries=None):
		self.seq = reference #either a sequence or an automat
		self.entries = entries if entries else set() #set of FeatureInstances

	def __str__(self):
		out = self.seq[:50] + '...' + self.seq[-50:] + ' ' + str(len(self.seq)) + 'bp\n' if len(self.seq) >200 else self.seq + ' ' + str(len(self.seq)) + 'bp\n'
		for fi in self.entries:
			out += '\t' + str(fi) + '\t' + str(fi.seq) +'\n'
		return out

	def add(self, entry):
		self.entries.add(entry)

	def remove(self, entry):
		self.entries.remove(entry)

	def __len__(self):
		return len(self.entries)

	def __iter__(self):
		for entry in self.entries:
			yield entry

	def turn(self):
		self.seq = rev_comp(self.seq)
		for fi in self.entries:
			fi.seq.turn()

	def alignments_to_entry(self, ref_fi):
		'''return dictionary: alignments between each FI and the given FI'''
		'''called for s_start_SF while SF merging'''
		'''given ref_fi is always original sequence (forward)''' 
		if ref_fi in self.entries:
			ref_seq = ref_fi.seq.seq(self.seq)
			result_dic = {}
			for fi in self.entries:
				if fi != ref_fi:
					ref_ops = list(ref_fi.seq.ops)
					new_ops = new_ops_from_ops(ref_ops, list(fi.seq.ops), self.seq) #ops for alignment fi.seq rebased on ref_fi.seq
					new_ops = ali_refinement(ref_seq,new_ops)
					result_dic[fi] = new_ops
		return result_dic


	def treat_empty_seq(self):
		entries = list(self.entries)
		ref_entry = entries[0]
		entries = entries[1:]
		ref_seq = ref_entry.seq.seq('')
		ref_entry.seq.ops = [len(ref_seq)]
		for entry in entries:
			entry.seq = editops_from_seqs(ref_seq, entry.seq.seq(entry.sh_feat.seq), reverse=entry.seq.reverse)
		self.seq = ref_seq

	def singleton_sf(self, chroms):
		'''returns True if all chromosomes given in set chroms are NOT covered, i.e. SF is a valid part of a singleton region'''
		for entry in self:
			if entry.chrom in chroms:
				return False
		return True


if __name__ == "__main__":
	pass
