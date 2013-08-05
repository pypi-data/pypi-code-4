"""High level OpenERP assertions and helpers."""


class OpenErpAssertions(object):
    """Mixin class providing assertion and helper methods to write tests.

    Some of these methods will make less sense with the new API scheduled for
    OpenERP 8, we'll provide them as simple wrappers for backwards compat then.
    """

    def _model_inst(self, model):
        return self.registry(model) if isinstance(model, basestring) else model

    def searchUnique(self, model, domain, **kw):
        """Search, assert that there's exactly one result, return its id.

        :model: can be either a string (model name) or a model instance
        :domain: domain to perform the search with
        :kw: any additional keyword (e.g., ``context``) is passed both
             to search or read.
        """
        model = self._model_inst(model)
        ids = model.search(self.cr, self.uid, domain, **kw)
        self.assertEquals(len(ids), 1,
                          msg="Domain %r on model %r should give "
                          "exactly one record "
                          "(got %d)" % (domain, model, len(ids)))
        return ids[0]

    def readUnique(self, model, domain, load='_classic_write', **kw):
        """Fetch a record by domain, assert unicity, return a read.

        :model: can be either a string (model name) or a model instance
        :load: directly passed to the underlying ``read`` call.
        :kw: any additional keyword (e.g., ``context``) is passed both
             to search or read.
        """
        model = self._model_inst(model)
        rec_id = self.searchUnique(model, domain, **kw)

        return model.read(self.cr, self.uid, rec_id, load=load, **kw)

    def assertRecord(self, model, rec_id, vals, list_to_set=False, **kw):
        """Fetch and compare a record with the provided values dict.

        This saves a LOT of typing and makes assertion much easier to read
        while avoiding a browse.

        :model: can be either a string (model name) or a model instance
        :rec_id: numeric id of the record to check
        :vals: ``dict`` of expected values. For ``many2one`` fields, just pass
               the expected numeric id.
        :list_to_set: if ``True``, all ``list`` instances in the read record
                      will be converted to ``set`` prior tocomparison
        :kw: any additional keyword arguments are passed on to the underlying
             call(s) of ``assertEqual``.

        Examples:

         - if you already have the model obj as ``users_model``::

             self.assertRecord(users_model, 1, dict(name='Administrator'))

         - in general::

             self.assertRecord('res.users', 1, dict(name='Administrator',
                                                    partner_id=1))
        """
        def normalize(v):
            if list_to_set and isinstance(v, list):
                return set(v)
            return v

        read = dict((k, normalize(v))
                    for k, v in self._model_inst(model).read(
                        self.cr, self.uid, rec_id, vals.keys(),
                        load='_classic_write').iteritems()
                    if k in vals)
        self.assertEqual(read, vals, **kw)
