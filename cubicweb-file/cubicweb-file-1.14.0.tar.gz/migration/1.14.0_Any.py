add_attribute('File', 'data_sha1hex')

if confirm('compute sha1sum for each File ?', default='n'):
    for entity in rql('Any X,D WHERE X is File, X data D').entities():
        entity.cw_set(data_sha1hex=entity.compute_sha1hex())
    commit()
