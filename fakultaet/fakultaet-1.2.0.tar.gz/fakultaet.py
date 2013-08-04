'''
Created on 04.08.2013

@author: Dogan
'''
def fak_rek(n):
    if(n<=1):
        return 1
    else:
        return n*fak_rek(n-1)

def fak_iter(n):
    if(n<=1):
        return 1
    else:
        prod=1
        for i in range(2,n+1):
            prod=prod*i
        return prod
    