from itertools import izip
from .tasks import Task

__all__ = ['find_variable_lengths']

#TODO NOT WORKING
def find_lengths(data, find_vars, _lock):
    m = None
    with data.rows._row_lock:
        m = data.rows.create_mark('Finding variable lengths')
    
    class FindVarLengthsTask(Task):
        #TODO MAKE THIS ONLY CHECK STRING VARIABLE LENGTHS
        #TODO figure out how to return the len_dict
        def __init__(self, _variables):
            self.len_dict = {}
            def func(row):
                for var, v_name in izip(row, (n.name for n in _variables)):
                    l = len(repr(var))
                    if v_name not in  self.len_dict:
                         self.len_dict[v_name] = l if var else 1
                    else:
                        if var and l >  self.len_dict[v_name]:
                             self.len_dict[v_name] = l

            Task.__init__(self, func, 'Finding variable lengths', m)             
    
    x = FindVarLengthsTask(find_vars)
    data.add_task(FindVarLengthsTask(find_vars))
    print x.len_dict
    return x.len_dict
    

def find_variable_lengths(data, variables, lock = False):
    """Returns a dictionary of variable lengths for the supplied varaible set.
    The keys of the dictionary are variable names and the values are the max found
    within the dataset.
    
    variables: A cardsharp VariableSet object. If no VariableSet supplied then defaults
    to full VariableSet of the current dataset.
    
    """
    find_lengths(data, variables, lock)