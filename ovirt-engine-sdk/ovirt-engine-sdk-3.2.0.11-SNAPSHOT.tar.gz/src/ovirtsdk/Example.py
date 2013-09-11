from ovirtsdk.xml import params
from ovirtsdk.infrastructure.context import context
from ovirtsdk.api import API
import socket
import gc


# gc.set_debug(gc.DEBUG_LEAK)
#
# class Foo:
#     def __init__(self, x):
# #         print "Foo: Hi"
#         self.x = x
#     def __del__(self):
#         print "%s.__del__" % self
#
# class Fa:
#     def __init__(self):
# #         print "Fa: Hi"
#         self.foo = Foo(self)
#
#     def __del__(self):
#         print "%s.__del__" % self
#
# class Foo2:
#     def __del__(self):
#         print "%s.__del__" % self
#
#
# fa = Fa()
#
# for i in range(100):
#     globals()['var' + str(i)] = Fa()

# gc.collect()

# try:
#     api = API(url='http://localhost:8080/api', username='admin@internal', password='letmein!')
# finally:
#     api.disconnect()

# api.disconnect()

#
# a = API(url='http://localhost:8080/api', username='admin@internal', password='letmein!')
# b = API(url='http://localhost:8080/api', username='admin@internal', password='letmein!')
# c = API(url='http://localhost:8080/api', username='admin@internal', password='letmein!')
# d = API(url='http://localhost:8080/api', username='admin@internal', password='letmein!')

with API(url='http://localhost:8080/api', username='admin@internal', password='letmein!', debug=False, session_timeout= -1) as api:
    h_list = api.hosts.list()
    stats_to_show = ['cpu.current.system', 'cpu.current.idle']
    for h in h_list:
        statistics = h.statistics.list()
        for statistic in statistics:
            if statistic.get_name() in stats_to_show:
                print "%s=%0.4f %s" % (
                                    statistic.get_name(),
                                    statistic.get_values().get_value()[0].datum ,
                                    statistics[0].get_unit()
                )


    # api.disconnect()
    #
    # api = API(url='http://localhost:8080/api', username='admin@internal', password='letmein!')
    #
#     print api.clusters.list()
    #
    # api = API(url='http://localhost:8080/api', username='admin@internal', password='letmein!')
    #
    # api.clusters.list()
    #
    # api4 = API(url='http://localhost:8080/api', username='admin@internal', password='letmein!')
    #
    # api4.clusters.list()
    #
    # api5 = API(url='http://localhost:8080/api', username='admin@internal', password='letmein!')
#
#     api5.clusters.list()





#     print context.manager[id(api)].get('entry_point')
#
#     params.Action(vm=params.VM(disks=params.Disks(disk=[params.Disk()])))
#
#     f = file()
