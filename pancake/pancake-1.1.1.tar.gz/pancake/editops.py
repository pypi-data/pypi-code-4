#from pancake.utils import *
from pancake.utils import needle_wunsch

import sys

class EditOps:

	def __init__(self, ops, reverse=False):
		self.ops = ops # list of edit operations
		self.reverse = reverse #indicates if editoperation should be applied to ref seqquence or its reverse complement


	def __str__(self):
		if self.reverse:
			return '-' + ''.join(map(lambda x: -x*'.' if type(x)==int and x< 0 else str(x), self.ops))
		else:
			return ''.join(map(lambda x: -x*'.' if type(x)==int and x< 0 else str(x), self.ops))


	def __len__(self):
		'''return length of resulting sequence'''
		l = 0
		for op in self.ops:
			if type(op) == int:
				if op>0: l += op
			else: l += 1
		return l


	#used for tests and divide
	def ref_len(self):
		'''return length of corresponding reference sequence'''
		l = 0
		for op in self.ops:
			if type(op) == int:
				l+=abs(op)
			elif op.isupper():
				l += 1
		return l


	def list_ops(self):
		'''convert edit ops string into list'''
		l, dels = [], 0
		for i in self.ops:
			if dels and i != '.':
				l.append( -dels)
				dels=0
			if i.isdigit():
				if l and type(l[-1]) == str and l[-1].isdigit():
					l[-1] += i
				else:
					l.append(i)
			elif i == '.':
				dels += 1
			else:
				l.append(i)
		if dels:
			l.append( -dels)
		#convert matches into int types
		self.ops = list(map(lambda o: int(o) if type(o)==str and o.isdigit() else o, l))


	#used for turnSF
	def turn(self):
		self.ops = [x if type(x)==int else rev_comp(x) for x in self.ops[::-1]]
		self.reverse = not self.reverse


	def divide(self, cut_ind):
		'''return two new EditOps Objects, cut_ind represents cut_ind in corresponding ref_seq!'''
		'''call for NON_REFERENCE FeatureInstance in divideSF'''
		length = 0
		ops1, ops2 = [], [] #edit operation lists of new EditOps
		self_ops = self.ops
		for i in range(len(self_ops)):
			if length >= cut_ind:
				ops2 = self_ops[i:]
				break
			ops1.append(self_ops[i])
			#compute new length
			if type(self_ops[i]) == int:
				length += abs(self_ops[i])
			elif self_ops[i].isupper():
				length += 1
		op1, op2 = EditOps(ops1, self.reverse), EditOps(ops2, self.reverse)
		op1_ref_len = op1.ref_len()
		if op1_ref_len > cut_ind:
			if ops1[-1] > 0:
				op2.ops = [op1_ref_len-cut_ind] + ops2
				op1.ops[-1] = ops1[-1] - op1_ref_len + cut_ind #i.e. op1.ops[-1] = ops1[-1] - (op1_ref_len - cut_ind)
			else:
				#ops1 ends with deletion
				op2.ops = [cut_ind-op1_ref_len] + op2.ops #i.e. op2.ops = [-1*(op1_ref_len-cut_ind)] + op2.ops
				op1.ops[-1] = ops1[-1] + op1_ref_len - cut_ind # i.e. -1 * (ops1[-1] - (op1_ref_len - cut_ind))
		return op1, op2


	def ref_cut_ind_and_ref_ops(self, overlap):
		'''return cut_ind of reference sequence, overlap is always from the start of self.ops'''
		'''return cut_ind parameter for self.divide()'''
		c, lops,i = 0, 0,0
		for op in self.ops:
			if lops >= overlap:
				break
			i+=1
			if type(op) == int:
				if op > 0:
					c+=op
					lops+=op
				else:
					c+=abs(op)
			elif op.isupper():
				c+=1
				lops+=1
			elif op.islower():
				lops += 1
		new1,new2 = EditOps(self.ops[:i] ,self.reverse), EditOps(self.ops[i:], self.reverse)
		if lops>overlap:
			c = c-(lops-overlap)
			new1.ops[-1] = new1.ops[-1]-(lops-overlap)
			new2.ops = [lops-overlap] + new2.ops
		return c, new1,new2



	def seq(self, ref_seq):
		''' return dna sequence encrypted by edit_op '''
		seq=[]
		seq_ind = 0
		for item in self.ops:
			if type(item) == int:
				if item >0:
					#matches
					seq.append(ref_seq[seq_ind:seq_ind+item])
					seq_ind+=item
				else:
					#deletions
					seq_ind += abs(item)
			elif item.islower():
				#insertion
				seq.append(item.upper())
			else:
				#substitution
				seq.append(item)
				seq_ind += 1
		seq = ''.join(seq)
		return seq


	def get_alignment(self, ref_seq):
		'''return alignment'''
		ref_ali_seq = ''
		ali_seq = ''
		seq_ind = 0
		for item in self.ops:
			if type(item) == int:
				if item >0:
					#matches
					ref_ali_seq += ref_seq[seq_ind:seq_ind+item]
					ali_seq += ref_seq[seq_ind:seq_ind+item]
					seq_ind += item
				else:
					#deletions
					ref_ali_seq += ref_seq[seq_ind:seq_ind+abs(item)]
					ali_seq += abs(item) * '-'
					seq_ind += -item
			elif item.islower():
				#insertion
				ref_ali_seq += '-'
				ali_seq += item.upper()
			else:
				#substitution
				ref_ali_seq += ref_seq[seq_ind]
				ali_seq += item.upper()
				seq_ind += 1
		return (ref_ali_seq, ali_seq)


	#get rid of subsequent match ops
	#TODO avoid this call
	def treat_double_matches(self):
		i =1
		while i<len(self.ops):
			if (type(self.ops[i-1]), type(self.ops[i])) == (int,int) and self.ops[i-1]>0 and self.ops[i]>0:
				self.ops[i-1] += self.ops[i]
				self.ops = self.ops[:i] + self.ops[i+1:]
			else: i+=1


def editops_from_ali(q_string, s_string, reverse=True):
	'''return EditOps Instance computed from given alignment, EditOps represents sequence in s_string'''
	'''s_string is assumed to be already reverse complement, if reverse_flag set'''
	matches, deletions, ops = 0, 0, []
	for qs, ss in zip(q_string, s_string):
		if qs.upper() == ss.upper():
			matches+=1
			if deletions>0: 
				ops.append(-deletions)
				deletions=0
		else:
			if matches>0:
				ops.append(matches)
				matches=0
			if ss == '-':
				deletions+=1
			else:
				if deletions>0:
					ops.append(-deletions)
					deletions=0
				if qs == '-':
					ops.append(ss.lower())
				else:
					ops.append(ss.upper())
	if matches>0:
		ops.append(matches)
	if deletions >0: ops.append(-deletions)
	return EditOps( ops, reverse)


def editops_from_seqs(ref_seq, seq, reverse=False):
	'''return EditOps Instance computed from the alignment of the given sequences, EditOps represents seq'''
	'''if reverse: seq already have to be reverse complement'''
	q_string, s_string = needle_wunsch(ref_seq,seq)
	return editops_from_ali(q_string, s_string, reverse)

def rev_comp(s):
	return s.translate(str.maketrans('ACGTacgtRYMKrymkVBHDvbhd', 'TGCAtgcaYRKMyrkmBVDHbvdh'))[::-1]



if __name__ == "__main__":
	pass


