from wheelcms_axle.themes import Theme, theme_registry

themes = (
            ('amelia', 'Amelia'),
            ('cerulean', 'Cerulean'),
            ('cosmo', 'Cosmo'),
            ('cyborg', 'Cyborg'),
            ('flatly', 'Flatly'),
            ('journal', 'Journal'),
            ('readable', 'Readable'),
            ('simplex', 'Simplex'),
            ('slate', 'Slate'),
            ('united', 'United'))

for id, name in themes:
    theme_registry.register(Theme(id, name, "%s-bootstrap.min.css" % id))

