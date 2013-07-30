import test_sum_primes
import parakeet 

n = 3 
expected = test_sum_primes.sum_primes(n)
parakeet.find_broken_transform(test_sum_primes.sum_primes, [n], expected)
