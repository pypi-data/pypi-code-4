#!/usr/bin/env python
# -*- coding:utf-8 -*-


from functor import F, run, lift, c_, call
from list import L


x = F('abc')
y = x >> str.upper >> (lambda x: x + 'def')
y.run()
run(y)
y()

x = F(3) >> (lambda x: x + 1)
y = F(5) >> (lambda x: x ** 2)
z = lift(lambda x, y: x + y)(x, y)
z()


run(len << F('abcde'))


with F(0):
    def f(x):
        return x + 10
    def b(x):
        return x * 2
    def c(x):
        print('val: %s' % x)
        

with F(123) as box:
    def f(x):
        return x % 7
    def b(x):
        return x * 2
box.value
run(box >> (lambda x: x * 2))


run(F(range(10)) >> c_(map)(lambda x: x * 2)
                 >> c_(filter)(lambda x: x < 7)
                 >> c_(sorted).key(lambda x: -x))

with F(range(10)) as box:
    @c_(map)
    def f(x):
        y = x % 3
        z = x + y
        return x + y + z
    @c_(sorted, keyword='key')
    def g(x):
        return (x % 7, x % 3, x)
print(box.value)

run(L([1, 2, 3]) >> (lambda x: x + 1))


with F('abc') as box:
    box.call(str.upper)
    box.call(lambda x: x + 'def')
print(box.value)


def deco(f):
    def _(x):
        return f(x)
    return _

with F('abc') as box:
    @call
    @deco
    def f(x):
        return x + 'def'
print(box.value)


f = lift(lambda x, y: (x, y)) 
f(L(range(3)), L('ab'))()
