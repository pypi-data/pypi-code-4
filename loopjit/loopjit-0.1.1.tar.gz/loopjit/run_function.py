
import llvm_backend
from llvm_backend import ctypes_to_generic_value, generic_value_to_python 
from llvm_backend.llvm_context import global_context     

from ndtypes import type_conv 
from transforms import pipeline 

def run(fn, args, exec_engine = global_context.exec_engine):
  actual_types = tuple(type_conv.typeof(arg) for arg in  args)
  expected_types = fn.input_types
  assert actual_types == expected_types, \
    "Arg type mismatch, expected %s but got %s" % \
    (expected_types, actual_types)
  
  lowered_fn = pipeline.lowering.apply(fn)
  llvm_fn = llvm_backend.compile_fn(lowered_fn).llvm_fn  
        
  # calling conventions are that output must be preallocated by the caller'
  ctypes_inputs = [t.from_python(v) for (v,t) in zip(args, expected_types)]
  gv_inputs = [ctypes_to_generic_value(cv, t) for (cv,t) in
               zip(ctypes_inputs, expected_types)]

  gv_return = exec_engine.run_function(llvm_fn, gv_inputs)
  return generic_value_to_python(gv_return, fn.return_type)