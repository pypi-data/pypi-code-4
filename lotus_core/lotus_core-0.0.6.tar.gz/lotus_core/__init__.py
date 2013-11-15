
import lotus_core_hpp

from mixin_core          import *
from read_basis_DATA     import *
from impl_wrapper4lapack import *

def vector2list(vec):
  N = len(vec)
  li = []
  for i in range(N):
    li.append(vec[i])
  return li

def list2vector_int(li):
  N = len(li)
  vec = lotus_core_hpp.get_vector_int(N)
  for i in range(N):
    vec[i] = li[i]
  return vec

def list2vector_double(li):
  N = len(li)
  vec = lotus_core_hpp.get_vector_double(N)
  for i in range(N):
    vec[i] = li[i]
  return vec


 

 
