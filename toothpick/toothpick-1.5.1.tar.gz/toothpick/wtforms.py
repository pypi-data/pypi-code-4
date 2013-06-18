
def populate(model, form, resource=None):
    for name, field in form._fields.iteritems():
        if resource:
            model.add_field(resource, **{name: field.data})
        else:
            setattr(model, name, field.data)
        

