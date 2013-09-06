from pancake.utils import rev_comp

#from utils import rev_comp

class FeatureInstance:

	def __init__(self, chrom, start=None, stop=None, seq =None, sh_feat=None, nextFI=None, prevFI=None):
		self.sh_feat = sh_feat
		self.start = start
		self.stop = stop
		self.nextFI = nextFI
		self.prevFI = prevFI
		self.chrom = chrom
		self.seq= seq #either sequence, or EditOps


	def __str__(self):
		out = '{}\t{}-{}\t'.format(self.chrom, str(self.start), str(self.stop))
		out += '-' if self.sh_feat and self.seq.reverse else '+'
		#out += '\t' + str(fi.seq)
		return out


	def sequence(self):
		#returns original genomic sequence between start and stop
		if self.sh_feat:
			s = self.seq.seq(self.sh_feat.seq) if not self.seq.reverse else rev_comp(self.seq.seq(self.sh_feat.seq))
			return s
		else:
			return self.seq

if __name__ == "__main__":
	pass
