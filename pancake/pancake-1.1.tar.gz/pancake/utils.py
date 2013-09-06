import numpy
#from editops import *

#scores for needle wunsch alignment
match_score = 10
mm_score = -5
gap_score = -5 #for opening and extending 


###

def rev_comp(s):
	return s.translate(str.maketrans('ACGTacgtRYMKrymkVBHDvbhd', 'TGCAtgcaYRKMyrkmBVDHbvdh'))[::-1]


def delete_gaps(seq):
	return seq.replace('-','')

####alignment modifications

def needle_wunsch(s1, s2):

	m,n = len(s1),len(s2)
	table = numpy.zeros((m+1, n+1)) #DP table

	# fill table
	for i in range(0, m+1): table[i][0] = gap_score * i
	for j in range(0, n+1): table[0][j] = gap_score * j
	for i in range(1, m+1):
		for j in range(1, n+1):
			match = table[i-1][j-1] + score(s1[i-1], s2[j-1])
			delete = table[i-1][j] + gap_score
			insert = table[i][j-1] + gap_score
			table[i][j] = max(match, delete, insert)

	#traceback
	ali1, ali2 = '', ''
	i,j = m,n # start from bottom right
	while i > 0 and j > 0:
		current = table[i][j]
		diagonal = table[i-1][j-1]
		up = table[i][j-1]
		left = table[i-1][j]

		if current == diagonal + score(s1[i-1], s2[j-1]):
			ali1 += s1[i-1]
			ali2 += s2[j-1]
			i -= 1
			j -= 1
		elif current == left + gap_score:
			ali1 += s1[i-1]
			ali2 += '-'
			i -= 1
		elif current == up + gap_score:
			ali1 += '-'
			ali2 += s2[j-1]
			j -= 1

	#continue to top left cell
	while i > 0:
		ali1 += s1[i-1]
		ali2 += '-'
		i -= 1
	while j > 0:
		ali1 += '-'
		ali2 += s2[j-1]
		j -= 1
	return(ali1[::-1], ali2[::-1])


def score(b1, b2):
	if b1 == b2: 
		return match_score
	elif b1 == '-' or b1 == '-':
		return gap_score
	else:
		return mm_score


def get_new_alignment(ali1, ali2):
	#return (heuristic) alignment of 2nd sequence in ali1 and 2nd sequence in ali2
	#returns only 'gapped' sequences, not an Alignment instance
	ali1_ind = 0
	ali2_ind = 0
	new_alignment = [ [], [] ]
	lali1, lali2 = len(ali1[0]), len(ali2[0])
	ali1_0, ali1_1, ali2_0, ali2_1 = ali1[0], ali1[1], ali2[0], ali2[1]
	while ali1_ind < lali1 and ali2_ind < lali2:
		if ali1_0[ali1_ind] != '-':
			if ali2_0[ali2_ind] != '-':
				#prevent "double gaps"
				if ali1_1[ali1_ind] != '-' or ali2_1[ali2_ind] != '-':
					new_alignment[0].append(ali1_1[ali1_ind])
					new_alignment[1].append(ali2_1[ali2_ind])
				ali1_ind += 1
				ali2_ind += 1
			else:
				# gap in ali2_0
				new_alignment[0].append('-')
				new_alignment[1].append(ali2_1[ali2_ind])
				ali2_ind += 1
		else:
			# gap in ali1_0
			if ali2_0[ali2_ind] != '-':
				new_alignment[0].append(ali1_1[ali1_ind])
				new_alignment[1].append('-')
				ali1_ind += 1
			else:
				#gap in ali2_0
				#prevent "double gaps"
				if ali1_1[ali1_ind] != '-' or ali2_1[ali2_ind] != '-':
					new_alignment[0].append(ali1_1[ali1_ind])
					new_alignment[1].append(ali2_1[ali2_ind])
				ali1_ind += 1
				ali2_ind += 1

	a1 = ''.join(new_alignment[0])
	a2 = ''.join(new_alignment[1])
	
	#remaining bases?
	if ali1_ind < lali1: 
		a1 += ali1_1[ali1_ind:]
		a2 += '-' * (lali1 - ali1_ind)
	if ali2_ind < lali2: 
		a2 += ali2_1[ali2_ind:]
		a1 += '-' * ( lali2 - ali2_ind)

	return (a1, a2 )


def ali_rev_comp(ali):
	#get reverse complement of 2 aligned sequences
	new1 = ali[0].translate(str.maketrans('ACGTacgtRYMKrymkVBHDvbhd', 'TGCAtgcaYRKMyrkmBVDHbvdh'))[::-1]
	new2 = ali[1].translate(str.maketrans('ACGTacgtRYMKrymkVBHDvbhd', 'TGCAtgcaYRKMyrkmBVDHbvdh'))[::-1]
	return (new1, new2)

def new_ops_from_ops(op1,op2,ref):
	#op1,op2=editops corresponding to ref
	#return new representaion of op2 corresponding to op1
	ref_ind, op1_ind, op2_ind = 0,0,0
	new_op2 = []
	op2_match, op2_del = 0,0
	while op1_ind < len(op1) and op2_ind<len(op2):
		if type(op1[op1_ind]) == int:
			if op1[op1_ind] > 0:
				#match
				if type(op2[op2_ind]) == int:
					if op2[op2_ind]>0:
						#match,match --> match in new_op2
						if op2_del: 
							new_op2.append(-op2_del)
							op2_del = 0
						match_len = min(op1[op1_ind], op2[op2_ind])
						ref_ind += match_len
						op2_match += match_len
						if op1[op1_ind] > match_len:
							op1[op1_ind] -= match_len
						else: op1_ind +=1
						if op2[op2_ind] > match_len:
							op2[op2_ind] -= match_len
						else: op2_ind +=1
					elif op2[op2_ind]<0:
						#match,del --> deletion in new_op2
						if op2_match: 
							new_op2.append(op2_match)
							op2_match = 0
						del_len = min(op1[op1_ind], -op2[op2_ind])
						ref_ind += del_len
						op2_del += del_len
						if op1[op1_ind] > del_len:
							op1[op1_ind] -= del_len
						else: op1_ind +=1
						if -op2[op2_ind] > del_len:
							op2[op2_ind] += del_len
						else: op2_ind +=1
				else:
					if op2_del: 
						new_op2.append(-op2_del)
						op2_del = 0
					elif op2_match:
						new_op2.append(op2_match)
						op2_match = 0
					if op2[op2_ind].isupper():
						#match, substitution --> substitution in new_op2
						ref_ind +=1
						if op1[op1_ind] >1:
							op1[op1_ind] -= 1
						else: op1_ind +=1
						new_op2.append(op2[op2_ind])
						op2_ind+=1
					elif op2[op2_ind].islower():
						#match,insertion --> insertion in new_op2
						new_op2.append(op2[op2_ind])
						op2_ind+=1
			else:
				#deletion
				if type(op2[op2_ind]) == int:
					if op2[op2_ind]>0:
						#deletion,match --> insertion in new_op2
						#
						if op2_del: 
							new_op2.append(-op2_del)
							op2_del = 0
						elif op2_match:
							new_op2.append(op2_match)
							op2_match = 0
						#
						del_length = min(-op1[op1_ind],op2[op2_ind])
						if -op1[op1_ind] > del_length:
							op1[op1_ind] += del_length
						else: op1_ind+=1
						for b in ref[ref_ind:ref_ind+del_length]:
							new_op2.append(b.lower())
						ref_ind += del_length
						if op2[op2_ind] > del_length:
							op2[op2_ind] -= del_length
						else:
							op2_ind+=1
					else:
						#deletion,deletion --> just skip
						del_length = min(-op1[op1_ind],-op2[op2_ind])
						if -op1[op1_ind] > del_length:
							op1[op1_ind] += del_length
						else: op1_ind+=1
						if -op2[op2_ind] > del_length:
							op2[op2_ind] += del_length
						else: op2_ind+=1
						ref_ind+=del_length
				else:
					#deletion, substitution --> insertion
					#deletion, insertion --> insertion
					if op2_del: 
						new_op2.append(-op2_del)
						op2_del = 0
					elif op2_match:
						new_op2.append(op2_match)
						op2_match = 0
						
					if op2[op2_ind].isupper():
						#deletion, substitution --> insertion
						if -op1[op1_ind]>1:
							op1[op1_ind] += 1
						else: op1_ind +=1
						ref_ind+=1
					new_op2.append(op2[op2_ind].lower())
					op2_ind+=1
					
		elif op1[op1_ind].isupper():
			#substitution
			if type(op2[op2_ind]) == int:
				if op2[op2_ind]>0:
					#subtitution, match --> substitution in op2
					if op2_del: 
						new_op2.append(-op2_del)
						op2_del = 0
					elif op2_match:
						new_op2.append(op2_match)
						op2_match = 0
					new_op2.append(ref[ref_ind])
					if op2[op2_ind] > 1:
						op2[op2_ind] -=1
					else: op2_ind+=1
					ref_ind+=1
					op1_ind+=1
				else:
					#substitution, deletion --> deletion in op2
					if op2_match:
						new_op2.append(op2_match)
						op2_match = 0
					if -op2[op2_ind] > 1:
						op2[op2_ind]+=1
					else: op2_ind+=1
					ref_ind+=1
					op1_ind+=1
					op2_del+=1
			elif op2[op2_ind].isupper():
				#substitution, substitution --> match or substitution
				if op2_del: 
					new_op2.append(-op2_del)
					op2_del = 0
				#
				if op1[op1_ind]==op2[op2_ind]:
					op2_match+=1
				else:
					if op2_match:
						new_op2.append(op2_match)
						op2_match = 0
					new_op2.append(op2[op2_ind])
				op1_ind+=1
				op2_ind+=1
				ref_ind+=1
			else:
				#substitution,insertion --> insertion
				if op2_del: 
					new_op2.append(-op2_del)
					op2_del = 0
				elif op2_match:
					new_op2.append(op2_match)
					op2_match = 0
				#
				new_op2.append(op2[op2_ind])
				op2_ind+=1
		else:
			#insertion
			if type(op2[op2_ind]) == int:
				if op2[op2_ind]>0:
					#insertion, match --> deletion in op2
					if op2_match:
						new_op2.append(op2_match)
						op2_match = 0
					op2_del+=1
				else:
					#insertion, deletion -->  deletion in op2
					if op2_match:
						new_op2.append(op2_match)
						op2_match = 0
					op2_del+=1
				op1_ind+=1
			elif op2[op2_ind].isupper():
				#insertion, substitution --> deletion #TODO think about
				if op2_match:
					new_op2.append(op2_match)
					op2_match = 0
				op2_del +=1
				op1_ind+=1
			else:
				#insertion, insertion --> match or substitution
				if op2_del: 
					new_op2.append(-op2_del)
					op2_del = 0
				if op1[op1_ind]==op2[op2_ind]:
					#match
					op2_match+=1
				else:
					#substitution
					if op2_match:
						new_op2.append(op2_match)
						op2_match = 0
					#
					new_op2.append(op2[op2_ind].upper())
				op1_ind+=1
				op2_ind+=1

	
	if op2_match:
		new_op2.append(op2_match)
		op2_match = 0
		
	#treat remaining ops in op1 (insertions)
	for op in op1[op1_ind:]:
		op2_del += 1
	if op2_del: new_op2.append(-op2_del)

	#remaining ops in op2 are exclusively insertions (only present if no remaining ops in op1)
	for op in op2[op2_ind:]:
		new_op2.append(op)


	remaining_dels = len(ref[ref_ind:])
	if type(new_op2[-1]) == int and new_op2[-1] < 0:
			new_op2[-1] -= remaining_dels
	elif remaining_dels>0:
		new_op2 += [-remaining_dels]

	#TODO check while building
	i =1
	while i<len(new_op2):
		if (type(new_op2[i-1]), type(new_op2[i])) == (int,int) and new_op2[i-1]>0 and new_op2[i]>0:
			new_op2[i-1] += new_op2[i]
			new_op2 = new_op2[:i] + new_op2[i+1:]
		else: i+=1

	return new_op2


def ali_refinement(seq,ops):
	#align regions between matches correctly by needle_wunsch
	i = 0
	seq_ind, seq_l = 0, 0
	prev_op_ind = 0
	while i < len(ops):
		if type(ops[i]) == int:
			if ops[i]>0:
				#match
				if i >0:
					tmp_ops = ops[prev_op_ind:i]
					tmp_ali = ali_from_ops(tmp_ops, seq[seq_ind:seq_ind+seq_l])
					new_ali = needle_wunsch(tmp_ali[0].replace('-',''), tmp_ali[1].replace('-',''))
					new_tmp_ops = ops_from_ali(new_ali[0], new_ali[1])
					seq_ind += seq_l+ops[i]
					seq_l=0
					if prev_op_ind>0 and new_tmp_ops and ( type(ops[prev_op_ind-1]), type(new_tmp_ops[0])) == (int, int) and ops[prev_op_ind-1] >0 and new_tmp_ops[0] >0:
						ops[prev_op_ind-1] += new_tmp_ops[0]
						new_tmp_ops = new_tmp_ops[1:]
					if i < len(ops)-1 and new_tmp_ops and (type(ops[i]), type(new_tmp_ops[-1]))== (int,int) and ops[i] >0 and new_tmp_ops[-1]>0:
						ops[i] += new_tmp_ops[-1]
						new_tmp_ops = new_tmp_ops[:-1]
					ops = ops[:prev_op_ind] + new_tmp_ops + ops[i:] if prev_op_ind >0 else new_tmp_ops + ops[i:]
					#original
					prev_op_ind = prev_op_ind + len(new_tmp_ops) +1
					i= prev_op_ind-1 #is incremented at END of WHILE
					if len(new_tmp_ops)==0 and prev_op_ind>1:
						#take care of
						#AC-A
						#A-CA ---> three subsequent matches
						if type(ops[prev_op_ind-2])==int and ops[prev_op_ind-2] >0: # and type(ops[prev_op_ind-1])==int and ops[prev_op_ind-1] >0:
							#ops[prev_op_ind-1] is already known to be a match?
							ops[prev_op_ind-2] += ops[prev_op_ind-1]
							ops = ops[:prev_op_ind-1] + ops[prev_op_ind:]
							prev_op_ind -=1
							i-=1
				else: 
					prev_op_ind+=1
					seq_ind = ops[i]

			else:
				#deletion
				seq_l += abs(ops[i])
		elif ops[i].isupper():
			#substitution
			seq_l+=1
		else:
			#insertion
			pass
		i+=1
	#final
	if prev_op_ind < i-1:
		#print('final')
		tmp_ops = ops[prev_op_ind:]
		tmp_ali = ali_from_ops(tmp_ops, seq[seq_ind:])
		new_ali = needle_wunsch(tmp_ali[0].replace('-',''), tmp_ali[1].replace('-',''))
		new_tmp_ops = ops_from_ali(new_ali[0], new_ali[1])
		ops = ops[:prev_op_ind] + new_tmp_ops
	return ops


def ali_from_ops(ops, ref_seq):
	'''return alignment'''
	ref_ali_seq = ''
	ali_seq = ''
	seq_ind = 0
	for item in ops:
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
	return ref_ali_seq, ali_seq

def ops_from_ali(q_string, s_string):
	'''return EditOps ops computed from given alignment, ops represents sequence in s_string'''
	'''s_string is assumed to be already reverse complement, if reverse_flag set'''
	matches, deletions, o = 0, 0, []
	for qs, ss in zip(q_string, s_string):
		if qs.upper() == ss.upper():
			matches+=1
			if deletions>0: 
				o.append(-deletions)
				deletions=0
		else:
			if matches>0:
				o.append(matches)
				matches=0
			if ss == '-':
				deletions+=1
			else:
				if deletions>0:
					o.append(-deletions)
					deletions=0
				if qs == '-':
					o.append(ss.lower())
				else:
					o.append(ss.upper())
	if matches>0:
		o.append(matches)
	if deletions >0: o.append(-deletions)
	return o


def ops_from_ops_and_ali(ops, seq, qstring,sstring):
	#ops == editops for rebasing qstring to seq
	#return new_ops rebasing sequence of sstring to seq
	new_ops, ops_ind = [], 0
	seq_ind = 0
	matchs, dels=0,0
	#treat preceding deletions
	if type(ops[ops_ind]) == int and ops[ops_ind] < 0:
		dels += -ops[ops_ind]
		seq_ind+=-ops[ops_ind]
		ops_ind+=1
	for qs,ss in zip(qstring, sstring):
		if ops_ind < len(ops):
			if qs!= '-' and ss == '-':
				#deletion in ref_ali
				if type(ops[ops_ind]) == int:
					if ops[ops_ind]>0:
						#deletion in ref_ali, match in ops --> deletion in new_ops
						if matchs:
							new_ops.append(matchs)
							matchs=0
						dels+=1
						if ops[ops_ind]>1:
							ops[ops_ind]-=1
						else: ops_ind+=1
						seq_ind+=1
					else:
						pass #Should not happen
				elif ops[ops_ind].islower():
					#deletion in ref_ali, insertion in ops --> skip
					ops_ind+=1
				else:
					#deletion in ref_ali, substituion in ops --> deletion in new_ops
					if matchs:
						new_ops.append(matchs)
						matchs=0
					dels+=1
					#divide case for increment of seq_ind
					seq_ind+=1
					ops_ind+=1
			elif qs== '-' and ss != '-':
				#insertion in ref_ali --> always insertion in new_ops
				if dels:
					new_ops.append(-dels)
					dels=0
				elif matchs:
					new_ops.append(matchs)
					matchs=0
				new_ops.append(ss.lower())
			elif qs == ss:
				#match in ref_ali
				if type(ops[ops_ind]) == int:
					if ops[ops_ind]>0:
						#match in ref_ali, match in ops --> match in new_ops
						if dels:
							new_ops.append(-dels)
							dels=0
						matchs+=1
						seq_ind+=1
						if ops[ops_ind]>1:
							ops[ops_ind]-=1
						else: ops_ind+=1
					#else: #There should never be deletions
						#pass #TODO
						#match in ref_ali, deletion ops
				else:
					if dels:
						new_ops.append(-dels)
						dels=0
					elif matchs:
						new_ops.append(matchs)
						matchs=0
					if ops[ops_ind].islower():
						##match in ref_ali, insertion in ops --> insertion in new_ops
						new_ops.append(ss.lower())
						ops_ind+=1
					else:
						##match in ref_ali, substitution in ops --> substituion in new_ops
						new_ops.append(ss)
						ops_ind+=1
						seq_ind+=1
			else:
				#substituion in ref_ali
				if type(ops[ops_ind]) == int:
					if ops[ops_ind]>0:
						#substituion in ref_ali, match in ops --> substituion in new_ops
						if dels:
							new_ops.append(-dels)
							dels=0
						elif matchs:
							new_ops.append(matchs)
							matchs=0
						new_ops.append(ss)
						if ops[ops_ind]>1:
							ops[ops_ind]-=1
						else: ops_ind+=1
						seq_ind+=1
					else: pass
						#TODO should never be the case
				elif ops[ops_ind].islower():
					#substituion in ref_ali, insertion in ops --> insertion in new_ops
					if dels:
						new_ops.append(-dels)
						dels=0
					elif matchs:
						new_ops.append(matchs)
						matchs=0
					new_ops.append(ss.lower())
					ops_ind+=1
				else:
					#substituion in ref_ali, substituion in ops --> match or substitution in new_ops
					if dels:
						new_ops.append(-dels)
						dels=0
					if ss==seq[seq_ind]:
						#match
						matchs+=1
					else:
						#substitution
						if matchs:
							new_ops.append(matchs)
							matchs=0
						new_ops.append(ss)
					seq_ind+=1
					ops_ind+=1
			#TODO maybe treat 'double-gaps'
			#treat deletions in ops
			if ops_ind<len(ops) and type(ops[ops_ind])==int and ops[ops_ind]<0:
				if matchs:
					new_ops.append(matchs)
					matchs=0
				dels+= -ops[ops_ind]
				seq_ind += -ops[ops_ind]
				ops_ind+=1
		else:
			#ops closed
			#remaining ali should contain insertions exclusively
			if matchs:
				new_ops.append(matchs)
				matchs=0
			elif dels:
				new_ops.append(-dels)
				dels=0
			new_ops.append(ss.lower())
	####END ZIP
	
	if matchs:
		new_ops.append(matchs)
	elif dels:
		new_ops.append(-dels)
	return new_ops



def turn_ops(seq, ops):
	#return ops rebasing sequence of seq to the sequence given by ops
	seq_ind=0
	ops_ind=0
	new_ops = []
	matchs, dels = 0, 0
	for op in ops:
		if type(op)==int:
			if op>0:
				#match --> match
				if dels:
					new_ops.append(-dels)
					dels=0
				new_ops.append(op)
				seq_ind+=op
			else:
				#deletion --> insertion
				if dels:
					new_ops.append(-dels)
					dels=0
				for s in seq[seq_ind:seq_ind+(-op)]: new_ops.append(s.lower())
				seq_ind+=-op
		elif op.islower():
			#insertion --> deletion
			dels+=1
		else:
			#substituion --> substituion
			if dels:
				new_ops.append(-dels)
				dels=0
			new_ops.append(seq[seq_ind])
			seq_ind+=1
	if dels:
		new_ops.append(-dels)
	return new_ops


if __name__ == "__main__":
	pass

