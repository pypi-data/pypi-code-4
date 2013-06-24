class Serializable(object):

    def __getstate__(self):
        return dict(
            docs=self._docs,
            meta=dict(
                _new_documents=self._new_documents,
            ),
            transients=dict(
                (name, getattr(self, name))
                for name in getattr(self, 'transients', [])
                if hasattr(self, name)
            ),
        )

    def __setstate__(self, state):
        self._docs = state['docs']
        self._new_documents = state['meta']['_new_documents']
        [setattr(self, name, value) 
         for (name, value) in state['transients'].items()]

