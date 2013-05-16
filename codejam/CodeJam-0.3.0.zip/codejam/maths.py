from math import *
import random

_smallprimeset = 1000000
def primes_below(N):
    if N < _smallprimeset:
        return [n for n in smallprimes if n < N]
    correction = N % 6 > 1
    N = {0:N, 1:N - 1, 2:N + 4, 3:N + 3, 4:N + 2, 5:N + 1}[N % 6]
    sieve = [True] * (N // 3)
    sieve[0] = False
    for i in xrange(int(N**0.5) // 3 + 1):
        if sieve[i]:
            k = (3 * i + 1) | 1
            sieve[k * k // 3::2 * k] = [False] * ((N // 6 - (k * k) // 6 - 1) // k + 1)
            a, b = (k * k + 4 * k - 2 * k * (i % 2)) // 3, 2 * k
            sieve[a::b] = [False] * ((N // 6 - (k * k + 4 * k - 2 * k * (i % 2)) // 6 - 1) // k + 1)
    return [2, 3] + [(3 * i + 1) | 1 for i in xrange(1, N // 3 - correction) if sieve[i]]

smallprimes = primes_below(_smallprimeset)
smallprimeset = set(smallprimes)

def is_prime(n, precision = 7):
    if n <= 1 or n % 2 == 0:
        return False
    elif n < _smallprimeset:
        return n in smallprimeset

    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1

    for repeat in range(precision):
        a = random.randrange(2, n - 2)
        x = pow(a, d, n)

        if x == 1 or x == n - 1: continue

        for r in range(s - 1):
            x = pow(x, 2, n)
            if x == 1: return False
            if x == n - 1: break
        else: return False

    return True

def pollard_brent(n):
    if n % 2 == 0: return 2
    if n % 3 == 0: return 3

    y, c, m = random.randint(1, n-1), random.randint(1, n-1), random.randint(1, n-1)
    g, r, q = 1, 1, 1
    while g == 1:
        x = y
        for i in range(r):
            y = (pow(y, 2, n) + c) % n

        k = 0
        while k < r and g == 1:
            ys = y
            for i in range(min(m, r-k)):
                y = (pow(y, 2, n) + c) % n
                q = q * abs(x-y) % n
            g = gcd(q, n)
            k += m
        r *= 2
    if g == n:
        while True:
            ys = (pow(ys, 2, n) + c) % n
            g = gcd(abs(x - ys), n)
            if g > 1:
                break

    return g

def prime_factors(n, sort = False):
    factors = []

    limit = int(n**0.5) + 1
    for checker in smallprimes:
        if checker > limit: break
        while n % checker == 0:
            factors.append(checker)
            n //= checker
            limit = int(n**0.5) + 1
            if checker > limit: break

    if n < 2: return factors

    while n > 1:
        if is_prime(n):
            factors.append(n)
            break
        factor = pollard_brent(n) # trial division did not fully factor, switch to pollard-brent
        factors.extend(prime_factors(factor)) # recurse to factor the not necessarily prime factor returned by pollard-brent
        n //= factor

    if sort: factors.sort()

    return factors

def factors(n):
    f = factorisation(n)
    F = [1]
    for p in f.keys():
        new = [[q * p**(i + 1) for q in F] for i in range(f[p])]	
        F += sum(new, [])
    return sorted(F)
	
def factorisation(n):
    factors = {}
    for p1 in prime_factors(n):
        try:
            factors[p1] += 1
        except KeyError:
            factors[p1] = 1
    return factors

totients = {0: 1}
def totient(n):
    if n not in totients:
        tot = 1
        for p, exp in factorisation(n).items():
            tot *= (p - 1)  *  p**(exp - 1)

        totients[n] = tot
    return totients[n]

def gcd(a, b):
    if a == b: return a
    while b > 0: a, b = b, a % b
    return a

def lcm(a, b):
    return abs(a * b) // gcd(a, b)

def xgcd(a,b):
    """xgcd(a,b) returns a list of form [g,x,y], where g is gcd(a,b) and
    x,y satisfy the equation g = ax + by."""
    a1=1; b1=0; a2=0; b2=1; aneg=1; bneg=1
    if(a < 0):
        a = -a; aneg=-1
    if(b < 0):
        b = -b; bneg=-1
    while (1):
        quot = -(a // b)
        a = a % b
        a1 = a1 + quot*a2; b1 = b1 + quot*b2
        if(a == 0):
            return [b, a2*aneg, b2*bneg]
        quot = -(b // a)
        b = b % a;
        a2 = a2 + quot*a1; b2 = b2 + quot*b1
        if(b == 0):
            return [a, a1*aneg, b1*bneg]

def choose(n, r, p):
    if not is_prime(p):
        raise ValueError('Modulo value must be prime')
        
    return _choose(n, r, p, lambda x: pow(x, p - 2, p))

def _choose(n, r, p, inv):
    if n > p:
        return _choose(n % p, r % p, p, inv) * _choose(n / p, r / p, p, inv)

    choices = 1
    for i in range(n - r + 1, n + 1):   choices = (choices * i) % p
    for i in range(1, r + 1):           choices = (choices * inv(i)) % p
    return choices % p

def choose(n, r):
    choices = 1
    for i in range(n - r + 1, n + 1):   choices *= i
    for i in range(1, r + 1):           choices /= i
    return choices

def pow(a, n, m):   # calculates a**n mod m
    result = a**0
    while n:
        if n & 1:
            result = (result * a) % m
        n >>= 1
        a = (a * a) % m
    return result