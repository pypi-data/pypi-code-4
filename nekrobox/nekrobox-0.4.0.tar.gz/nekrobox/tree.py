from .docdecs import params


@params(layers=(dict, "Dictionary tree"),
        path=(list, "Path to walk down"),
        returns=(tuple, "The leaf and remainder of the path."))
def path_walker(layers, path):
    """Recursively walk the given path and return what is left.

    Walk through the given ``layers``, a dictionary tree, recursively until a
    `leaf` (anything that is not a dictionary) is found at which time it is
    returned along with any left over parts of the path.
    """
    head, tail = path[0], path[1:]
    branch = layers[head]
    if isinstance(branch, dict):
        return path_walker(branch, tail)
    else:
        return (branch, tail)


@params(tree=(dict, "Dictionary tree to modify"),
        path=(list, "Branch path to add the ``leaf`` too"),
        key=(object, "Key for the new leaf"),
        leaf=(object, "To be added to the tree. This should not be a dict."),
        returns=(dict, "Returns the modified tree"))
def tree_add(tree, path, key, leaf):
    """Add a new leaf to the tree.

    Adds the given ``leaf`` object to the ``tree`` under the given ``path``
    which will be constructed as needed.
    """
    branch = tree
    for item in path:
        if not item in branch:
            branch[item] = {}
        branch = branch[item]

    branch[key] = leaf
    return tree
