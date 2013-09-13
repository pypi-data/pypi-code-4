def kwargs_to_string(**kwargs):
    def joiner(key, value):
        if type(value) == bool and value or value is None:
            return key
        return '%s=%s' % (key, value)
    return ' '.join(['--%s' % joiner(key, value) for (key, value) in kwargs.items()])


def pg_dump_command(*args, **kwargs):
    return 'pg_dump %s' % kwargs_to_string(**kwargs)


def pg_restore_command(*args, **kwargs):
    return 'pg_restore %s' % kwargs_to_string(**kwargs)
