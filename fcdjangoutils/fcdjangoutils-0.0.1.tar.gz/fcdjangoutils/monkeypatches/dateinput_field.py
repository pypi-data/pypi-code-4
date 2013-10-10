import django.forms

def merge_dicts(appends, *ds):
    res = dict(ds[0])
    for d in ds[1:]:
        res.update(d)
    for name, sep in appends.iteritems():
        values = [d[name]
                  for d in ds
                  if name in d]
        if values:
            res[name] = sep.join(values)
    return res

def build_attrs(self, extra_attrs=None, **kwargs):
    "Helper function for building an attribute dictionary."    
    class_name = ("%s.%s" % (type(self).__module__, type(self).__name__)).replace('.', '_').lower()
    return merge_dicts({'class': ' '}, {'class': class_name}, self.attrs, kwargs, extra_attrs or {})
django.forms.Widget.build_attrs = build_attrs
