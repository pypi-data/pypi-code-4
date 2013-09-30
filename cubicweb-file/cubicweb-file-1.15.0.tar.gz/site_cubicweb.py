options = (
    ('image-max-size',
     {'type' : 'string',
      'default': None,
      'help': 'all images will be resized to this max size if set',
      'group': 'file',
      'level': 2,
      }),
    ('image-thumb-size',
     {'type' : 'string',
      'default': '75x75',
      'help': 'thumbnail size of your images',
      'group': 'file',
      'level': 2,
      }),
    ('thumbnail-cache-directory',
     {'type':'string',
      'default': None,
      'help': ('Cache directory for thumbnails (if unset, defaults '
               'to INSTANCEDIR/cache/file/thumbnails) '
               'if set, must be an absolute path).'),
      'level': 2,
      'group': 'file'
      }),
    ('compute-sha1hex',
     {'type' : 'yn',
      'default': False,
      'help': 'compute sha1 hex digest of your files',
      'group': 'file',
      'level': 2,
      }),
    )


