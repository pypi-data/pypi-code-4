from parakeet import jit
import numpy as np

vects  = np.random.randn(40000, 10)

@jit
def allpairs_cosine(X,Y):
    def cosine(x,y):
        return np.dot(x, y) / (np.sqrt(np.dot(x, x)) * np.sqrt(np.dot(y, y))) 
    return np.array([[cosine(x,y) for y in Y] for x in X ])
 
@jit
def allpairs_euclid(X,Y):
    def euclid(x,y):
        return np.sum( (x-y)**2 )
    return np.array([[euclid(x,y) for y in Y] for x in X])
 
result = allpairs_cosine(vects,vects)
