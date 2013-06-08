from astkit import ast

from runnynose.tracker import get_record
from runnynose.tracker import get_setup

class TrackingTransformer(ast.NodeTransformer):
    
    def process(self, module):
        return self.visit(module)
    
    def visit_Module(self, module):
        self.generic_visit(module)
        setup = get_setup()
        if module.body:
            for node in setup:
                ast.copy_location(node, module.body[0])
            
            futures = []
            while (isinstance(module.body[0], ast.ImportFrom) 
                   and (module.body[0].module == '__future__')):
                futures.append(module.body.pop(0))
            module.body = futures + setup + module.body
        else:
            module.body = setup
        return module
    
    def visit_FunctionDef(self, defn):
        self.generic_visit(defn)
        record = get_record()
        for node in record:
            ast.copy_location(node, defn.body[0])
        defn.body = record + defn.body
        return defn
