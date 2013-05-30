import os

def get_config(fn):
  config = {}
  try:
    # get config
    with open(os.path.expanduser('~/%s' % fn), 'r') as f:
      args = [line.replace('\n','').split('=') for line in f.readlines()]
      for k, v in args:
        config[k] = v
  except OSError:
    # fn doesn't exist
    print "%s not found. Creating..." % fn
  finally:
    # error checking
    new_config = config.copy()
    for param in ['FC_KEY', 'DB_URI', 'DB_NAME', 'DB_USER', 'DB_PASS']:
      if param not in new_config:
        new_config[param] = raw_input("%s:" % param)

    # if config and new_config differ,
    # write new_config to fn
    if config != new_config:
      with open(os.path.expanduser('~/%s' % fn), 'w') as f:
        for k, v in new_config.items():
          f.write("%s=%s" % (k, v))
    return new_config