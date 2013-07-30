import numpy as np 
# import test_ufunc_math
import parakeet 


expected = np.logaddexp(0.4, 0.5)
parakeet.find_broken_transform(np.logaddexp, [0.4, 0.5], expected)
