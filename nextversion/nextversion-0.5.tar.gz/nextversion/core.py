# -*- coding: utf-8 -*-
import verlib


def nextversion(current_version):
    """Returns incremented module version number."""
    norm_ver = verlib.suggest_normalized_version(current_version)
    if norm_ver is None:
        return None
    norm_ver = verlib.NormalizedVersion(norm_ver)

    # increment last version figure
    parts = norm_ver.parts   # see comments of `verlib.py` to get the idea of `parts`
    assert(len(parts) == 3)
    if len(parts[2]) > 1:    # postdev
        if parts[2][-1] == 'f':  # when `post` exists but `dev` doesn't
            parts = _mk_incremented_parts(parts, part_idx=2, in_part_idx=-2, incval=1)
        else:                    # when both `post` and `dev` exist
            parts = _mk_incremented_parts(parts, part_idx=2, in_part_idx=-1, incval=1)
    elif len(parts[1]) > 1:  # prerel
        parts = _mk_incremented_parts(parts, part_idx=1, in_part_idx=-1, incval=1)
    else:                    # version & extraversion
        parts = _mk_incremented_parts(parts, part_idx=0, in_part_idx=-1, incval=1)
    norm_ver.parts = parts

    return str(norm_ver)


def _mk_incremented_parts(parts, part_idx, in_part_idx, incval=1):
    in_part_idx %= len(parts[part_idx])  # for negative index

    new_part = []
    for i, e in enumerate(parts[part_idx]):
        new_part.append(e + incval if i == in_part_idx else e)

    # workaround for bug in verlib.NormalizedVersion.parts_to_str
    if new_part[-1] == verlib.FINAL_MARKER[0]:
        new_part.pop()

    new_part = tuple(new_part)

    new_parts = []
    for i, part in enumerate(parts):
        new_parts.append(new_part if i == part_idx else part)
    return tuple(new_parts)
