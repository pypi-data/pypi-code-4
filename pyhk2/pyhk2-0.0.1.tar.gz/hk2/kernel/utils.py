
#===========================================================

def dump_plugin_graph(habitat):
    """ Dumps plugin graph to string """
    
    ret = ''
    for c in habitat.getAllContracts():
        ret += '* %(contract)s\n' % {'contract' : c.__name__}
        for s in habitat.getServicesByContract(c):
            ret += '  - %(service)s\n' % {'service' : s.__name__}
    
    return ret
