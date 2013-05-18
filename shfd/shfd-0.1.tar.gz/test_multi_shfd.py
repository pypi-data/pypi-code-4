import shfd

interpreters = (
    'python2.6',
    'python2.7',
    'python3.1',
    'python3.2',
    'python3.3',
)

for python in interpreters:
    print "========== %s ==========" % python
    print shfd.cmd('%s test_shfd.py' % python, error_in_intput=True).run().out