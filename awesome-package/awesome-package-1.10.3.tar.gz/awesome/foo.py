__all__ = ['bar']


def is_awesome(name):

    if name == "python":
        return True

    if name == "ruby":
        return False

    raise ValueError("Unknown name '{}'".format(name))
