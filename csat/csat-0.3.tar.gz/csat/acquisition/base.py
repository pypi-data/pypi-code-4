from __future__ import absolute_import

import abc

from zope.interface import implementer, Interface

from twisted.plugin import IPlugin


class ICollectorFactory(Interface):
    pass


class ICollectorConfigurator(Interface):
    pass


@implementer(ICollectorConfigurator, IPlugin)
class ConfiguratorBase(object):
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def get_model(self):
        pass

    @abc.abstractmethod
    def get_command(self, model):
        pass

    @abc.abstractproperty
    def version(self):
        pass

    @abc.abstractproperty
    def name(self):
        pass

    @abc.abstractproperty
    def key(self):
        pass

    def run(self, request, model, remote):
        postback = model.create_postback_url(save=False)
        postback = request.build_absolute_uri(postback)
        command = self.get_command(model)
        model.running_instance_id = remote.runCollector(command, postback)
        model.set_running()


@implementer(ICollectorFactory, IPlugin)
class FactoryBase(object):
    """
    Base data collection class to implement an actual collector runner.

    The log and tasks attributes will be set by the enclosing Runner
    instance before calling the run method.
    """
    __metaclass__ = abc.ABCMeta

    def build_parser(self, parser):
        parser.add_argument('--version', action='version',
                            version='{} {}'.format(self.name, self.version))
        return parser

    @abc.abstractproperty
    def key(self):
        pass

    @abc.abstractproperty
    def version(self):
        pass

    @abc.abstractproperty
    def name(self):
        pass

    @abc.abstractmethod
    def build_collector(self, args):
        pass


class CollectorBase(ConfiguratorBase, FactoryBase):
    pass
