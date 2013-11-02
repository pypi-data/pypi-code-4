#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      Lenovo
#
# Created:     05-10-2013
# Copyright:   (c) Lenovo 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------


def main():
    pass

if __name__ == '__main__':
    main()

number=input("enter a number whose prime factors are to be found")
i=number
x=2
c=3
while(i!=1):
    if(number%i==0):
        c=0
        x=2
        while(x<=i):
            if(i%x==0):
                c+=1
            x+=1

        if(c<=1):
            number=number/i
            print(i)

    i-=1


