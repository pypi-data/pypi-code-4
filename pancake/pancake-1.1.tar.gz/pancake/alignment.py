import sys

class Alignment:

	def __init__(self, qname, sname, qtuple, stuple, alignment, qstrand=None, sstrand=None):
		self.qali = alignment[0].upper()
		self.qname = qname
		self.qstart, self.qstop, self.qstrand = get_ali_items(qtuple, qstrand)
		self.sali = alignment[1].upper()
		self.sname = sname
		self.sstart, self.sstop, self.sstrand = get_ali_items(stuple, sstrand)

	def __str__(self):
		out = '{}: ({}, {}) '.format(self.qname, self.qstart, self.qstop)
		out += '+\n' if self.qstrand else '-\n'
		out += '{}: ({}, {}) '.format(self.sname, self.sstart, self.sstop)
		out += '+\n' if self.sstrand else '-\n'
		out+= self.qali +'\n'
		out+= self.sali
		return out

	def convert(self):
		'''change query and subject'''
		self.qali, self.sali = self.sali, self.qali
		self.qname, self.sname = self.sname, self.qname
		self.qstart, self.sstart = self.sstart, self.qstart
		self.qstop, self.sstop = self.sstop, self.qstop
		self.qstrand, self.sstrand = self.sstrand, self.qstrand


	#q indicates if cut_ind correspond to query or subject
	#cut_ind is always from alignment start (neither its + or -)
	def divide(self, cut_ind, q=True):
		ref_ali, not_ref_ali = (self.qali, self.sali) if q else (self.sali, self.qali)
		ref_len, not_ref_len, i = 0, 0, 0

		while ref_len<cut_ind:
			#only non-deletions count to ref_len and not_ref_len
			ref_len += ref_ali[i] != '-'
			not_ref_len += not_ref_ali[i] != '-' 
			i+=1
		new_alignment = (self.qali[:i], self.sali[:i])
		#just changing ref_len and not_ref_len once (for speed reasons)
		if not q: ref_len, not_ref_len = not_ref_len, ref_len
		qtuple1, qtuple2 = None, None
		if ref_len>0 and not_ref_len>0:
			qtuple1 = (self.qstart, self.qstart+ref_len-1) if self.qstrand else (self.qstop-ref_len+1, self.qstop)
			stuple1 = (self.sstart, self.sstart+not_ref_len-1) if self.sstrand else (self.sstop-not_ref_len+1, self.sstop)
		if bool(filter(lambda x: x!= '-',self.qali[i:] )) and bool(filter(lambda x: x!= '-',self.sali[i:] )):
			qtuple2 = (self.qstart+ref_len, self.qstop) if self.qstrand else (self.qstart, self.qstop-ref_len)
			stuple2 = (self.sstart+not_ref_len, self.sstop) if self.sstrand else (self.sstart, self.sstop-not_ref_len)

		if qtuple1:
			new_ali = Alignment(self.qname, self.sname, qtuple1, stuple1, new_alignment, qstrand=self.qstrand, sstrand=self.sstrand)
		if qtuple2:
			self.qali, self.sali = self.qali[i:], self.sali[i:]
			self.qstart, self.qstop = qtuple2[0], qtuple2[1]
			self.sstart, self.sstop = stuple2[0], stuple2[1]

		if qtuple1 and qtuple2:
			return new_ali, self
		elif qtuple1:
			return new_ali, None
		elif qtuple2:
			return None, self
		else: return None, None


def get_ali_items(tuple, strand=None):
	if strand == None:
		strand = tuple[0] <= tuple[1] #True, if forward
	return (min(tuple), max(tuple), strand)

