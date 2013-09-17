from wheelcms_axle.themes import Theme, theme_registry

themes = (
            ('amelia', 'Amelia'),
            ('cerulean', 'Cerulean'),
            ('cosmo', 'Cosmo'),
            ('cyborg', 'Cyborg'),
            ('journal', 'Journal'),
            ('readable', 'Readable'),
            ('simplex', 'Simplex'),
            ('slate', 'Slate'),
            ('spruce', 'Spruce'),
            ('superhero', 'Superhero'),
            ('united', 'United'))

for id, name in themes:
    theme_registry.register(Theme(id, name, "%s-bootstrap.min.css" % id))

