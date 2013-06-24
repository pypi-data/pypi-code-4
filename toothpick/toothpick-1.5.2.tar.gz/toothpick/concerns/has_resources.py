import toothpick
from toothpick import exceptions

class HasResources(object):

    @classmethod
    def _resource(cls, resource_name, action=toothpick.DEFAULT):
        '''
        Convenience method to turn a resource name into a resource.  If
        'action' is provided, then this method will respect resource proxies.
        '''
        try:
            resource = cls._resources[resource_name]
        except KeyError, e:
            raise exceptions.ToothpickError(
                "Class '%s' has no resource '%s'" % (cls.__name__,
                                                     resource_name)
            )

        if action in resource.proxies:
            try:
                resource = cls._resources[resource.proxies[action]]
            except KeyError, e:
                raise exceptions.ToothpickError(
                    ("Proxied '%s' action on resource '%s' to " +
                     "nonexistent resource '%s'") % (action,
                                                     resource_name,
                                                     e.message)
                )

        return resource

