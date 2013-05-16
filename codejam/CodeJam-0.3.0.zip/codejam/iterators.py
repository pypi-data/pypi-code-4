from itertools import *

def multirange(*sizes):
    return product(*(range(n) for n in sizes))

def subsets(X):
    return chain([()], *(combinations(X, r + 1) for r, x in enumerate(X)))

def window(s, n):
	return s[i:i + n] for i in range(len(s) - n)

def chunks(s, n):
	return s[i:i + n] for i in range(0, len(s), n)