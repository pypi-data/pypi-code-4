def truncate(comment, size):
    """
    truncate a text at size, adding ...
    if first word itself is too long, truncate it adding '.'

    truncated result should not have a len <= 3
    """
    while ' ' in comment and len(comment) > size:
        newcomment = ' '.join(comment.split(' ')[:-1])
        if len(newcomment) <= 3:
            break
        elif newcomment == comment:
            comment = newcomment
            break
        elif len(newcomment) <= size:
            return  newcomment + '...'

        comment = newcomment

    if len(comment) > size:
        # if first word is too long
        if '-' in comment[3:]:
            comment = comment.split('-')[0]

        if len(comment) > size:
            comment = comment[:size]

        comment = comment + '.'

    return comment