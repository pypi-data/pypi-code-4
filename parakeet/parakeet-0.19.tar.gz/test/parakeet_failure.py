from parakeet import jit, config 
import numpy as np

config.backend = 'cuda' 
vects  = np.random.randn(400, 10)
@jit 
def allpairs_cosine(X,Y):
    def cosine(x,y):
        return np.dot(x, y) / (np.sqrt(np.dot(x, x)) * np.sqrt(np.dot(y, y))) 
    return np.array([[cosine(x,y) for y in Y] for x in X ])
 
 
print "Running python" 
python_result = allpairs_cosine.fn(vects,vects)
print "Running parakeet" 
parakeet_result = allpairs_cosine(vects, vects)

print python_result[:3]
print parakeet_result[:3]
assert np.allclose(python_result, parakeet_result) 
