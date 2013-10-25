from .config import CHECK_INDEX


def resume_status(index):
    try:
        chk = CHECK_INDEX[index].copy()
        inst = chk['type'](name=chk['name'], url=chk['url'], **chk.get('kwargs', {}))
        chk["result"] = inst.to_python()
        chk["result_instance"] = chk
        return chk
    except IndexError:
        return {}


def resume_statuses():
    """
    Return a dictionnary of Checkers with their results
    """
    return [resume_status(i) for i in range(0, len(CHECK_INDEX))]


def global_status(statuses):
    for s in statuses:
        try:
            if s['result']["is_valid"] is not True:
                return False
        except KeyError:
            return False
    return True
