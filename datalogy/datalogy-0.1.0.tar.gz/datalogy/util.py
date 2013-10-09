def extract(dictionary, keys):
    """
    Extract only the specified keys from a dict

    :param dictionary: source dictionary
    :param keys: list of keys to extract
    :return dict: extracted dictionary
    """
    return dict(
        (k, dictionary[k]) for k in keys if k in dictionary
    )


def get_default(row, index, default=None):
    try:
        return row[index]
    except IndexError:
        return default


def non_empty(row):
    return any([cell for cell in row])


def pad_list(row, length, missing_value=None):
    padding = length - len(row)
    if padding:
        padding = padding * [missing_value]
        return row + padding
    return row
