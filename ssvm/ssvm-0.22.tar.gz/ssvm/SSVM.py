#! /usr/bin/python
# -*- coding: utf-8 -*-


#If you have any questions, please contact any of the following:
#Evan(evan176@hotmail.com)


import sys, numpy

###############################################################################

#Use this class to do SSVM computing
#Input:
#A_pos, A_neg = must be numpy mxn array
#C = penalty in SVM
#w0, b0 = initial point in Newton method. w0 is nx1 array, b0 is float value

#-------------------------------------------------------------------------------

#使用這個class來作SSVM的計算
#輸入：
#A_pos, A_neg = 必須要是 numpy mxn array
#C = SVM中用來決定分錯的權重性
#w0, b0 = 牛頓法中的起始點  w0 is numpy nx1 array, b0 is float value

###############################################################################
class SSVM():
    def __init__(self, A_pos, A_neg, C, w0, b0, precision=1E-5, convergSpeed=1E-8):  
        #Initialize Trainer

    #Set limit on data matrix : A_pos and A_neg
        #設定矩陣 A_pos, A_neg 的限制
        if not isinstance(A_pos, numpy.ndarray) or not isinstance(A_neg, numpy.ndarray):
            print '\n===Error in SSVM-init : A_pos or A_neg must be 2d-array==='
            sys.exit(1)
        if A_pos.shape[1] != A_neg.shape[1]:
            print '\n===Error in SSVM-init : A_pos index must equal to A_neg==='
            sys.exit(1)

    #Set limit on parameter : C
        #設定參數 C 的限制
        if C <= 0 :
            print '\n===Error in SSVM-init : C must greater than 0==='
            sys.exit(1)

    #Set limit on parameter : w0
        #設定參數 w0 的限制
        if not isinstance(w0, numpy.ndarray) :
            print '\n===Error in SSVM-init : w0 must be array==='
            sys.exit(1)
        if w0.shape[0] <= 1 or w0.shape[1] > 1 :
            print '\n===Error in SSVM-init : w0 must be mx1 array==='
            sys.exit(1)

        self.precision = precision
        self.convergSpeed = convergSpeed
        self.A = numpy.vstack([numpy.hstack([A_pos, -numpy.ones([A_pos.shape[0], 1])]), numpy.hstack([-A_neg, numpy.ones([A_neg.shape[0], 1])])])
        self.C = C
        self.w = numpy.vstack((w0, b0))
            
        del(A_pos)
        del(A_neg)

###############################################################################

#Use this function to adjust parameters
#Input:
#precision = How precision we want in SSVM
#convergeSpeed = converge speed in Newton method

#-------------------------------------------------------------------------------

#使用這個含式來調整SSVM計算時的情況
#輸入：
#precision = 在SSVM的計算中想要作到多精確的地步
#convergeSpeed = 牛頓法的收斂速度

###############################################################################
    def argu_set(self, precision, convergeSpeed):

    #Set limit on parameter : precision
        #設定參數 precision 的限制
        if precision <= 0:
            print '\n===Error in SSVM-argu_set : precision can not <= 0==='
            sys.exit(1)
    #Set limit on parameter : convergeSpeed
        #設定參數 convergeSpeed 的限制
        if convergeSpeed <= 0:
            print '\n===Error in SSVM-argu_set : convergeSpeed can not <= 0==='
            sys.exit(1)

        self.precision = precision
        self.convergeSpeed = convergeSpeed

###############################################################################

#Evaluate the function value
#Input:
#w = vector in SVM
#Output:
#return = value

#-------------------------------------------------------------------------------

#評估function value
#輸入：
#w = SVM中的超平面向量
#輸出：
#return = 評估值

###############################################################################
    def objf(self, w):

    #Set limit on parameter : w
        #設定參數 w 的限制
        if not isinstance(w, numpy.ndarray):
            print '\n===Error in SSVM-objf : w must be 2d-array==='
            sys.exit(1)
        elif w.shape[0] <= 1 or w.shape[1] > 1:
            print '\n===Error in SSVM-objf : w must be mx1array==='
            sys.exit(1)
        else:
            temp = numpy.ones((self.A.shape[0], 1)) - numpy.dot(self.A, w) 
            v = numpy.maximum(temp, 0)
            return 0.5 * (numpy.dot(v.transpose(), v) + numpy.dot(w.transpose(), w) / self.C)


###############################################################################

#Use this function to avoid the local maximum(minimum) in Newton method
#Input:
#w = current point
#gap = defined in ssvm code
#obj1 = the object function value of current point
#Output:
#stepsize = stepsize for Newton method

#-------------------------------------------------------------------------------

#使用armijo來避免 Newton method 碰到 local maximum(minimum)
#輸入：
#w = 起始點
#gap = SSVM中定義的算距離
#obj1 = 現在向量點的目標含式值
#輸出：
#stepsize = 決定牛頓法的距離

###############################################################################
    def armijo(self, w, z, gap, obj1):

        diff = 0
        stepsize = 0.5 # we start to test with setpsize=0.5
        count = 1
        while diff  < -0.05 * stepsize * gap:
            stepsize = 0.5 * stepsize
            w2 = w + stepsize * z
            obj2 = self.objf(w2)
            diff = obj1 - obj2    
            count = count + 1
            
            if count > 20:
                break

        return stepsize


###############################################################################

#Use this function to start training
#Output:
#return = w + b 

#-------------------------------------------------------------------------------

#使用這個含式開始訓練資料
#輸出：
#return = w + b

###############################################################################
    def train(self):
        e = numpy.ones((self.A.shape[0], 1))
        flag = 1
        counter = 0
        while flag > self.precision:
            counter = counter + 1
            d = e - numpy.dot(self.A, self.w)
            Point = d[: , 0] > 0

            if Point.all == False:
                return

            hessian = numpy.eye(self.A.shape[1]) / self.C + numpy.dot(self.A[Point, : ].transpose(), self.A[Point, : ])
            gradz = self.w / self.C - numpy.dot(self.A[Point, : ].transpose(), d[Point])

            del(d)
            del(Point)


            if numpy.dot(gradz.transpose(), gradz) / self.A.shape[1] > self.precision:
                z = numpy.linalg.solve(-hessian, gradz)
                del(hessian) 
      
                obj1 = self.objf(self.w)     
                w1 = self.w + z
                obj2 = self.objf(w1)      
      
                if (obj1 - obj2) <= self.convergSpeed:
                    # Use the Armijo's rule           
                    gap = numpy.dot(z.transpose(), gradz) # Compute the gap       
                    # Find the step size & Update to the new point
                    stepsize = self.armijo(self.w, z, gap, obj1)
                    self.w = self.w + stepsize * z         
                else:
                    # Use the Newton method
                   self.w = w1  

                flag = numpy.linalg.norm(z) 
            else:      
                break
            
            if counter >= 150:
                break

        #print self.w.shape
        return {'w': self.w[0: self.w.shape[0] - 1], 'b': self.w[self.w.shape[0] - 1]}




########################################Test Area########################################

"""


A=array([[1,20000,3],[4,50,6],[6010,2,1]])
B=array([[563,7066,9],[3,4547275,8],[-1,0,1]])
C=0.1
w0=array([[-977],[10000],[1]])
b=0
x=SSVM(A,B,C,w0,b)
print x.train()
"""
#####http://mathesaurus.sourceforge.net/matlab-numpy.html#####

