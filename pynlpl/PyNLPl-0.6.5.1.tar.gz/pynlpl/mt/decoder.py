import numpy
from pynlpl.datatypes import PriorityQueue, Pattern

EOSPATTERN = Pattern() #TODO

class TranslationHypothesis:
    def __init__(self,parent, decoder, sourcepattern, sourceoffset, targetpattern, targetoffset, tscores):
        self.parent = parent
        self.sourcepattern = sourcepattern
        self.sourceoffset = sourceoffset
        self.targetpattern = targetpattern
        self.targetoffset = targetoffset
        assert(all( x<0 for x in tscores)) #must all be logprobs

        #precompute tscore
        self.tscore = 0
        for l, x in zip(decoder.tweights, tscores):
            self.tscore += l * x

        if self.parent:
            history = self.parent.gettranslation(decoder.lm.order-1)
        else:
            history = None

        self.lmscore = decoder.lweight * decoder.lm.score(targetpattern, history)

        self.computeinputcoverage(s)

        self.final = (self.inputcoverage.min() == 1)
        if self.final:
            self.lmscore += decoder.lweight * decoder.lm.scoreword(EOSPATTERN,self.gettranslation(decoder.lm.order-1))

    def computeinputcoverage(self, decoder):
        self.inputcoverage = np.zeros(len(self.input),dtype=bool)
        for i in range(self.sourceoffset, self.sourceoffset + len(self.sourcepattern)):
            self.inputcoverage[i] = True


    def gettranslation(self,requestn=99999):
        n = len(self.targetpattern)
        if requestn == n:
            return self.targetpattern
        elif requestn < n:
            return self.targetpattern[n-requestn:n]
        elif self.parent:
            return self.parent.gettranslation(requestn-n) + self.targetpattern
        else:
            return self.targetpattern

    def expand(self):


class StackDecoder:
    def __init__(self, input, translationtable, lm, stacksize, prunethreshold, tweights, dweight, lweight, dlimit):
        self.input = input
        self.translationtable = translationtable
        self.lm = lm
        self.stacksize = stacksize
        self.prunethreshold = prunethreshold
        self.tweights = tweights
        self.dweight = dweight
        self.lweight = lweight
        self.dlimit = dlimit


        self.stacks

    def decode(self):


class Stack(PriorityQueue):

    def __init__(self, decoder, index, stacksize, prunethreshold):
        self.decoder = decoder
        self.index = index
        self.stacksize = stacksize
        self.prunethreshold = prunethreshold
        super().__init__([],lambda x: x.score, False, stacksize)





