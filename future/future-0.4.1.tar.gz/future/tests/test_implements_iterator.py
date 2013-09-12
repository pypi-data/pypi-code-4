from future.utils import implements_iterator

@implements_iterator
class MyIter(object):
    def __next__(self):
        print('Next!')
    def __iter__(self):
        return self

itr = MyIter()
next(itr)
