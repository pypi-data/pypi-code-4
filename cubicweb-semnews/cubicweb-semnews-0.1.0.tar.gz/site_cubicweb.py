

###############################################################################
### SOURCE TYPES ##############################################################
###############################################################################

options = (
    ('articles-lang',
     {'type' : 'string',
      'default': 'fr',
      'help': 'Language of the articles to be used (e.g. in startup view).',
      'group': 'semnews', 'level': 2,
      }),
    ('articles-dataviz-limit',
     {'type' : 'int',
      'default': 40,
      'help': 'Number of articles to be used for some dataviz views.',
      'group': 'semnews', 'level': 2,
      }),
    ('startup-day-limit',
     {'type' : 'int',
      'default': 3,
      'help': 'Number of days to be used for the startup view.',
      'group': 'semnews', 'level': 2,
      }),
    ('startup-influent-limit',
     {'type' : 'int',
      'default': 12,
      'help': 'Number of influent entities to be shown in startup page.',
      'group': 'semnews', 'level': 2,
      }),
    )
