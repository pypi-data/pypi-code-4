
def get_minispec_vars():
    g_values = globals()
    if 'minispec_vars' not in g_values:
        g_values['minispec_vars'] = {}
    return g_values['minispec_vars']

def is_current_test_case():
    return 'current_test_case' in get_minispec_vars()

def get_current_test_case():
    return get_minispec_vars()['current_test_case']

def set_current_test_case(test_case):
    get_minispec_vars()['current_test_case'] = test_case
    return test_case

def get_current_test_method():
    return get_minispec_vars()['current_test_method']

def set_current_test_method(test_method):
    get_minispec_vars()['current_test_method'] = test_method
    return test_method
