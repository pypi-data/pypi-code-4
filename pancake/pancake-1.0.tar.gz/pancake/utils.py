import numpy


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


if __name__ == "__main__":
	pass
