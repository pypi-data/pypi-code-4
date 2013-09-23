#!/usr/bin/env python
# -*- coding:utf-8 -*-


from __future__ import print_function
from functor import F, run, lift, c_, call
from list import ListF


x = F(1)
print(x.run())
y = x >> (lambda x: x + 1)
print(y)
print(y.run())
z = (lambda x: x + 1) << x
print(z.run())
print(z())
print((F(10) >> (lambda x: x * 2)).run())
print((F([10, 5, 3, 8, 11]) >> sorted).run())

print(run(F(10) >> (lambda x: x * 2) >> (lambda x: x + 1)))

# Functorのデフォルト実装はIdentity
print(run(F(5) >> (lambda x: x + 1)) == run(F((lambda x: x + 1)(5))))

x = F(1) >> (lambda x: x + 1)
y = F('a') >> (lambda x: x + 'b')
f = lift(lambda x, y: '%s:%s' % (x, y))
print(f)
g = f(x, y) >> str.upper
print(g)
print(run(g))


x = ListF([1, 2, 3]) >> (lambda x: x + 1)
print(run(x))
y = ListF([1, 2]) >> (lambda x: x * 10)
print(run(y))
f = lift(lambda x, y: x + y)
print(f)
print(f(x, y))
print(run(f(x, y)))
for n in f(x, y):
    print(n)


# ListFはジェネレータを引数にしても動く
from itertools import count, takewhile
f = ListF(x for x in range(5)) >> (lambda x: x + 1)
print(f())
xs = ((print('debug: %s' % n), n)[1] for n in count(0))
f = ListF(xs) >> (lambda x: x + 1)
g = takewhile(lambda x: x < 10, f)
print(g)
print(list(g))


# with構文のサポート
with F(10) as f:
    def foo(x):
        return x + 1

    def bar(x):
        return x * 2
print(f())


def test():
    with ListF(x for x in range(10)) as f:
        def foo(x):
            return x + 1

        def bar(x):
            return x * 2
    print(f())
test()


f = F(range(10)) >> c_(map)(lambda x: x * 2) >> c_(filter)(lambda x: x < 7)
print(list(f()))
f = F(range(10)) >> c_(map)(lambda x: x * 2) >> c_(sorted).key(lambda x: -x)
print(list(f()))


def moge():
    with F(range(10)) as f:
        @c_(map)
        def foo(x):
            return x + 1
        @c_(sorted, keyword='key')
        def bar(x):
            return (x % 7, x % 3, x)
    print(f.value)
    with F(range(10)) as f:
        f.call(lambda xs: [100] + list(xs))
        f.call(sorted)
    print(f.value)
moge()


deco = lambda f: (lambda x: f(x))

with F('abc') as box:
    @call
    @deco
    def f(x):
        return x + 'def'
print(box.value)



x = (lambda x: x + 1) << F(10)
x.run()
