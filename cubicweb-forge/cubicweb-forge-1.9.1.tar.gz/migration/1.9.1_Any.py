if not rql('CWAttribute A WHERE A relation_type R, R name "icon_format", A from_entity E, E name "Project"'):
    add_attribute('Project', 'icon_format')
