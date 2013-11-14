def evaluate(node, context):
    if type(node) in (list, set, tuple):
        rule = node.pop(0)
        return DISPATCH.get(rule)(node, context)
    else:
        return node

def _evaluate_nodes(nodes, context):
    return [evaluate(node, context) for node in nodes]

def _rule_and(node, context):
    values = _evaluate_nodes(node, context)
    return all(values)

def _rule_or(node, context):
    values = _evaluate_nodes(node, context)
    return any(values)

def _rule_lt(node, context):
    left_value, right_value = _evaluate_nodes(node, context)
    return left_value < right_value

def _rule_gt(node, context):
    left_value, right_value = _evaluate_nodes(node, context)
    return left_value > right_value

def _rule_lte(node, context):
    return not _rule_gt(node, context)

def _rule_gte(node, context):
    return not _rule_lt(node, context)

def _rule_is(node, context):
    left_value, right_value = _evaluate_nodes(node, context)
    return left_value == right_value

def _get_nested_dict_value(context, path):
    result = context
    for segment in path.split('.'):
        result = result.get(segment)
    return result

def _rule_attr(node, context):
    attr_name = evaluate(node.pop(0), context)
    return _get_nested_dict_value(context, attr_name)

def _rule_eval(node, context):
    fn = _rule_attr([node.pop(0)], context)
    fn_args = _evaluate_nodes(node, context)

    return fn(*fn_args)

def _rule_includes(node, context):
    values = _evaluate_nodes(node, context)
    test_value = values[0]
    test_cases = values[1:]
    return test_value in test_cases

def _rule_excludes(node, context):
    return not _rule_includes(node, context)

DISPATCH = {
    'and': _rule_and,
    'or': _rule_or,
    'attr': _rule_attr,
    'eval': _rule_eval,
    'is': _rule_is,
    'lt': _rule_lt,
    'lte': _rule_lte,
    'gt': _rule_gt,
    'gte': _rule_gte,
    'includes': _rule_includes,
    'excludes': _rule_excludes,
}
