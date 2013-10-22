class RemoteModule(object):
    def __init__(self, proxy):
        self.proxy = proxy
        for class_name in self.proxy.classes():
            def meta_hack(local_class_name):
                def creator(*args):
                    instance_name = self.proxy.create(local_class_name, args)
                    remote_instance = getattr(self.proxy, instance_name)
                    return remote_instance
                return creator
            setattr(self, class_name, meta_hack(class_name))
