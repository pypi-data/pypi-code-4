
from treelike import * 
from ndtypes import * 

import analysis
import llvm 
import names
import prims 
import syntax 
import transforms

from analysis.syntax_visitor import SyntaxVisitor

from transforms.inline import Inliner
from transforms.pipeline_phase import Phase  
from transforms.simplify import Simplify
from transforms.builder import Builder  
from transforms.transform import Transform 

from run_function import run 
from build_function import build_fn 