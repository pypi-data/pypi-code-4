import os


CREATED = 0
DELETED = 1
MODIFIED = 2


def _walk(top, followlinks, prefix=None):
    try:
        names = os.listdir(top)
    except Exception:
        raise StopIteration()

    prefix = prefix or []

    yield os.path.sep.join(prefix), names

    for name in names:
        new_path = os.path.join(top, name)
        if not os.path.isdir(new_path):
            continue

        new_prefix = list(prefix)
        new_prefix.append(name)
        if followlinks or not os.path.islink(new_path):
            for root, files in _walk(new_path, followlinks, new_prefix):
                yield root, files


def make_snapshot(path, followlinks=False):
    """
    Creates a snapshot of the directory

    :param path:
        Path string to directory

    :param followlinks:
        Follow links when traversing through directories
    """

    if not os.path.isdir(path):
        raise ValueError('path argument should be a path to directory: {}'
                         .format(path))

    result = {}
    for prefix, files in _walk(path, followlinks):
        for f in files:
            p = os.path.join(prefix, f)
            fullpath = os.path.join(path, p)
            try:
                result[p] = os.stat(fullpath)
            except FileNotFoundError:
                pass

    return result


def snapshot_diff(s1, s2):
    """
    Finds a differences between two snapshots

    :param s1:
        Original snapshot

    :param s2:
        New snapshot

    :return:
        Returns a generator that yields changes between snapshots
        in the format ``tuple(change, path)``
    """

    for k, v in s1.items():
        if not k in s2:
            yield DELETED, k
        else:
            if v != s2[k]:
                yield MODIFIED, k

    for k, v in s2.items():
        if not k in s1:
            yield CREATED, k
