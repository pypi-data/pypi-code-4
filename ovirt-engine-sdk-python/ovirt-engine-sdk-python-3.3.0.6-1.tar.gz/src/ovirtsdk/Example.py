from ovirtsdk.xml import params
from ovirtsdk.infrastructure.context import context
from ovirtsdk.api import API
import socket
import gc

# gc.set_debug(gc.DEBUG_LEAK)

class Foo:
    def __init__(self, x):
#         print "Foo: Hi"
        self.x = x
    def __del__(self):
        print "%s.__del__" % self

class Fa:
    def __init__(self):
#         print "Fa: Hi"
        self.foo = Foo(self)

    def __del__(self):
        print "%s.__del__" % self

class Foo2:
    def __del__(self):
        print "%s.__del__" % self


fa = Fa()

for i in range(100):
    globals()['var' + str(i)] = Fa()

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

# with API(url='http://localhost:8080/api', username='admin@internal', password='letmein!', debug=True, session_timeout= -1) as api:

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
