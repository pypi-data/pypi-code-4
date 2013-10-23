"""
In data mining , when we want to build the decision tree,
we need to select the attribute with the highest information gain

Gain(A)=Info(D)-Info'A'(D),   [1]

which
Info'A'(D) = the info value after using A to split D into v partitions ,
Info(D) = summation of Prob.*log(Prob.) of each value of attribute

Because the Info(D) is hard and redundant to calculate, so I write a piece of
widget to calculate that.

It has two input variable, and return the info value of x and y

References:
[1] See the wikipedia about Information Gain:
http://en.wikipedia.org/wiki/Information_gain_in_decision_trees

"""
import math

def log2(x):
    return math.log(x)/math.log(2)

def info(x,y):
    if(x == 0 or y == 0):
        return 0
    else:
        z = x+y
    return -(x/z)*log2(x/z)-(y/z)*log2(y/z)

