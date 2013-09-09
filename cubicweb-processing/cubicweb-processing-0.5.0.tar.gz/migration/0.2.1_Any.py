if 'Study' in schema:
    rename_entity_type('Study', 'RunChain')
    add_relation_definition('RunChain', 'wiring', 'Wiring')
else:
    add_entity_type('RunChain')
