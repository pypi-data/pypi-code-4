import fnmatch


def omitnames(names, patterns, sort=True):
    """
    Given a collection (list, set) of ``names``, remove any that do NOT match the glob
    sub-patterns found in ``patterns`` (separated by whitespace). If ``sort``,
    returns a sorted list (the default); else return the remaining names in
    their original order. If patterns is false-y, just return names.
    """
    if not patterns:
        return names
    omitset = set()
    for pattern in patterns.split(' '):
        omitset.update(fnmatch.filter(names, pattern))
    if sort:
        return sorted(set(names) - omitset)
    else:
        result = []
        for name in names:
            if name not in omitset:
                result.append(name)
        return result


def typename(value):
    """
    Return the name of a type. Idiosyncratic formatting to show in order to
    provide the right information, but in the least verbose way possible.
    E.g. where Python would format `<type 'int'>` or `class '__main__.CName'>`
    or `<class 'module.submod.CName'>`, this function would return `<int>`,
    `<CName>`, and `<CName>` respectively. If a neat name cannot be returned,
    the default Python type formatting is used.
    """
    the_type = type(value)
    tname = getattr(the_type, '__name__', None)
    if tname:
        return '<' + tname + '>'
    else:
        return '{0!r}'.format(the_type)

    # TODO: consider if a shortened form of the standard formatting should be
    # provided, either instead or as an option (ie, showing the module home
    # of the type); counterargument: they can always show(type(x)) if they want
    # the full shebang
