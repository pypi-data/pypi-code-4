# -*- coding: utf-8 -*-
"""
Objet du registre des tâches
"""
class AlreadyRegistered(Exception):
    pass

class NotRegistered(Exception):
    pass

class QueueSite(object):
    """
    An QueueSite object encapsulates an instance of the queue application.
    """
    def __init__(self):
        self._registry = {} # model_class class -> admin_class instance

    def get_registry(self):
        return self._registry

    def register(self, job):
        """
        Registers the given model(s) with the given admin class.

        The model(s) should be Model classes, not instances.

        If an admin class isn't given, it will use ModelAdmin (the default
        admin options). If keyword arguments are given -- e.g., list_display --
        they'll be applied as options to the admin class.

        If a model is already registered, this will raise AlreadyRegistered.
        
        Job objects are registered with their ``__name__`` attribute as their registry 
        key.
        
        :type job: object `Sveetchies.django.queues.BaseJob`
        :param job: Job object to register
        """
        if job in self._registry:
            raise AlreadyRegistered('The model %s is already registered' % job.__name__)
        # Instantiate the admin class to save in the registry
        #self._registry[job] = admin_class(job, self)
        self._registry[job.__name__] = (job.label, job)

    def unregister(self, job):
        """
        Unregisters the given model(s).

        If a model isn't already registered, this will raise NotRegistered.
        
        :type job: object `Sveetchies.django.queues.BaseJob`
        :param job: Job object to unregister
        """
        if job not in self._registry:
            raise NotRegistered('The model %s is not registered' % job.__name__)
        del self._registry[job.__name__]

# This global object represents the default admin site, for the common case.
# You can instantiate QueueSite in your own code to create a custom admin site.
site = QueueSite()
