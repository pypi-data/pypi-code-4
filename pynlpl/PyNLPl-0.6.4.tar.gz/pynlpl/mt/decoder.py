import numpy
from pynlpl.datatypes import Pattern

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

        final = False
        #computeinputcoverage()

        if final:
            self.lmscore += decoder.lweight * decoder.lm.scoreword(EOSPATTERN,self.gettranslation(decoder.lm.order-1))

    def computeinputcoverage():


    def gettranslation(requestn=99999):
        n = len(self.targetpattern)
        if requestn == n:
            return self.targetpattern
        elif requestn < n:
            return self.targetpattern[n-requestn:n]
        elif self.parent:
            return self.parent.gettranslation(requestn-n) + self.targetpattern
        else:
            return self.targetpattern


class StackDecoder:



class Stack:
    def __init__(self, decoder, index, stacksize, prunethreshold):
        self.decoder = decoder
        self.index = index
        self.stacksize = stacksize
        self.prunethreshold = prunethreshold

    def add(hypothesis):

    def bestscore(self):

    def worstscore(self):

    def __len__(self):
        return len(self.contents)

    def clear(self):
        self.contents.clear()

    def __nonzero__(self): #python 2.x
        return bool(contents)

    def __bool__(self):
        return bool(contents)


    def prune():
        pass

    def recombine():
        pass

    def pop():



