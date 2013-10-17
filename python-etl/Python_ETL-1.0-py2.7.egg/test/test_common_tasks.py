from cardsharp.test import construct_random_dataset
from itertools import izip

def test_find_max_variable_lengths():
    ds = construct_random_dataset()
    
    len_dict1 = {}
    
    for row in ds:
        for var, v_name in izip(row, (n.name for n in ds.variables)):
            l = len(repr(var))
            if v_name not in len_dict1:
                len_dict1[v_name] = l if var else 1
            else:
                if var and l > len_dict1[v_name]:
                    len_dict1[v_name] = l
    print len_dict1
    print ds.find_max_variable_lengths(['a','b','c','d', 'e','f'])