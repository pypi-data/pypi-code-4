#! /usr/bin/python
# -*- coding: utf-8 -*-

#If you have any questions, please contact any of the following:
#Evan(evan176@hotmail.com)
    

import os, sys, numpy, time, cPickle, split, kernel, SSVM

###############################################################################

#Input:
#data = The data user want to compute in SVM, must be 2d-array
#label_pos = label column in data, must be integer and need to greater than 0

#-------------------------------------------------------------------------------

#輸入：
#data = 要在SVM中做計算的資料，這裡必須要是numpy中的2d-array
#label_pos = 第幾個欄位要拿來當成label(class)，此值必需要是整數且大於0

###############################################################################
class Trainer():
    def __init__(self, data, label_pos):

        try:
            self.label = data[ :, label_pos]
            self.data = numpy.hstack( ( data[ :, : label_pos ], data[ :, label_pos + 1 : ] ) )
        except:
            print "\n===Error in trainer-init : data must be numpy 2d array or label_pos out of index==="            
            return False
        #Swap data to disk to reduce memory limit
        #在這裡先將暫時不會用到的資料置換到硬體中以增加記憶體使用空間
        try:
            numpy.save( 'rawData', data )
            numpy.save('tempLabel',self.label)
            numpy.save('tempData',self.data)
        except:
            print "\n===Error in trainer-init : can't save temp data==="            
            return False     
       
        del(data)

        self.rawData = 'rawData.npy'
        self.tempLabel = 'tempLabel.npy'
        self.tempData = 'tempData.npy'
        
        self.rlabel = []
        self.rdata = []

        self.model = []

        self.handler = self.make() and self.tune()


###############################################################################

#Split data to reduced set or validation set
#Input:
#r : Ratio of data we want to use
#v : Number of slice in Crossvalidation

#-------------------------------------------------------------------------------

#在這裡將資料做分割，看是要做reduced set或者是validation set
#輸入：
#r : 要取出多少比例的資料作為reduced set
#v : 在CrossValidation要做的次數

###############################################################################

    def make(self, r=1, v=1):

        #self.setIndex is a dictionary which is composed of 'subset' and 'fold' , every fold has two part : 'train' and 'test'
        #self.setIndex是一個'字典'，在這裡面包含兩部份，subset儲存的是reduced set的index，fold儲存的是reduced set在切割成CrossValidation的set，每一fold都包含兩部份分別是'train' 'test'


        #Set limit on parameter : r
        #設定參數 r 的限制
        if r > 1 or r <= 0:
            print "\n===Error in trainer-make : r must <= 1 and > 0==="
            return False
        #Set limit on parameter : v
        #設定參數 v 的限制
        if not isinstance( v, int ) or v < 1:
            print "\n===Error in trainer-make : v must be int and >= 1==="
            return False

        #Call original data back from disk
        #將原始資料從硬體中置換回來做處理
        try:
            self.label = numpy.load(self.tempLabel)
            self.data = numpy.load(self.tempData)
        except:
            print "\n===Error in trainer-make : can't load tempData and tempLabel==="
            return False

        self.ratio = r
        self.numFold = v
        try:
            self.setIndex = split.splitData(self.label, self.ratio, self.numFold)
            self.rlabel = self.label[self.setIndex['subset']].reshape(len(self.setIndex['subset']), 1)
            self.rdata = self.data[self.setIndex['subset'], : ]
        except:
            print "\n===Error in trainer-make : data can't be splited==="
            return False

        #Free object which don't need
        #清除不會在用到的資料
        del(self.label)
        del(self.data)

        return True

###############################################################################

#Set the parameters
#Input:
#c = Betst important parameter of SVM, controling error
#g = 'Gamma' of rbf kernel
#k = kernel type, 0 -> linear, 1 -> nonlinear
#s = training strategy, 0 -> One-Against-One, 1 -> One-Against-Rest

#-------------------------------------------------------------------------------

#設定training時的參數
#輸入：
#c = 在SVM中控制penalty的參數
#g = RBF kernel中的gamma值
#k = 選擇要用linear或者nonlinear, 0 -> linear, 1 -> nonlinear
#s = 在多個類別時決定要怎樣去做SVM training, 0 -> One-Again-One, 1 -> One-Again-Rest

###############################################################################
    def tune(self, c=100, g=0.1, k=1, s=0):

        #Set limit on parameter : c
        #設定參數 c 的限制
        if c <= 0:
            print "\n===Error in trainer-tune : c must > 0==="
            return False
        else:
            self.C = c

        #Set limit on parameter : g
        #設定參數 g 的限制
        if g <= 0:
            print "\n===Error in trainer-tune : g must > 0==="
            return False
        else:
            self.gamma = g

        #Set limit on parameter : k
        #設定參數 k 的限制
        if k != 1 and k != 0:
            print "\n===Error in trainer-tune : k must equal to 0 or 1==="
            return False
        else:
            self.kernelType = k

        #Set limit on parameter : s
        #設定參數 s 的限制
        if s != 1 and s != 0:
            print "\n===Error in trainer-tune : s must equal to 0 or 1==="
            return False
        else:
            self.strategy = s

        return True

###############################################################################

#Start training from here
#Before using this function, you can use two functions : "initial", "setParams" 
#to adjust SVM
#Output:
#TErr -> training error
#VErr -> validation error

#-------------------------------------------------------------------------------

#使用這個函式開始訓練SVM，在這之前可以先用"intial"和"setParams"這兩個函式去調整SVM
#TErr -> 訓練時的錯誤，VErr -> 驗證時的錯誤
#輸出：
#TErr -> 訓練錯誤
#VErr -> 驗證錯誤

###############################################################################
    def train(self):
        self.model = []
        if self.handler == True:
            start_t = time.time()
            TErr = numpy.zeros((self.numFold, 1))
            VErr = numpy.zeros((self.numFold, 1))
            for ith in range(self.numFold):
                self.model.append(self.multiClassifier(ith))
                result = self.multiPredictor(ith, self.setIndex['fold'][ith]['train'])
                TErr[ith] = self.errorEstimate(self.setIndex['fold'][ith]['train'], result)
                result = self.multiPredictor(ith, self.setIndex['fold'][ith]['test'])
                VErr[ith] = self.errorEstimate(self.setIndex['fold'][ith]['test'], result)
            stop_t = time.time()

            print "\nTraining accuracy:\n"
            print 1 - TErr
            print "\nValidation accuracy:\n"
            print 1 - VErr
            print "\nTraining model using %f s..." %(stop_t - start_t)


            return [1 - numpy.mean(TErr), 1 - numpy.mean(VErr)]

        else:
            print "\n===Error in trainer-train : 'make' or 'tune' not correct==="
            return False
###############################################################################

#MultiClassifier means this classifier can be used in multi label dataset
#There are two method, first one is "One-Against-One" if self.strategy = 0, 
#second one is "One-Against-Rest" if self.strategy = 1
#Input:
#ith = the number of set in "CrossValidation"
#Output:
#model = store w of multi classifier

#-------------------------------------------------------------------------------

#這個函式代表可以去做多類別的分類，在SVM中多類別的分類有兩種一種是"One-Against-One"，
#另一種是"One-Against-Rest"
#而SSVM中，如果self.strategy = 0 代表是"One-Against-One"，如果self.strategy = 1 
#則是"One-Against-Rest"
#輸入：
#ith = 在CrossValidation第幾筆要做處理
#輸出：
#model = 包含了多類別分類的各組w

###############################################################################
    def multiClassifier(self, ith):

        #Get unique label from reduced label set
        #從reduced set中找出有哪些label
        label_var = numpy.unique(self.rlabel)

        #Build kernel matrix for ith reduced dataset
        #為ith reduced set建置出kernel matrix
        K = kernel.buildKernel(self.kernelType, self.gamma, self.rdata[self.setIndex['fold'][ith]['train'], :])

        model = {}


        #Here is "One-Against-One"
        #這邊是做 "One-Against-One"
        if self.strategy == 0:
            if K['flag'] == 'dual':
                for i in label_var:
                    model[i] = {}
                    for j in label_var[numpy.where(label_var == i)[0] + 1 : label_var.shape[0]]:
                        model[i][j] = {}
                        var_pos = [y for y, x in enumerate(self.rlabel[self.setIndex['fold'][ith]['train']]) if x == i]
                        var_neg = [y for y, x in enumerate(self.rlabel[self.setIndex['fold'][ith]['train']]) if x == j]
                        #From set catch two cluster with different label, give then positive and negative label, i -> A+, j -> A-
                        #從set找出兩種不同類別的資料，並給予不同的標籤以便等一下作運算 i -> positive, j -> negative
                        model[i][j]['col'] = var_pos + var_neg
                        ssvm = SSVM.SSVM(K['Kernel'][var_pos, : ][:, model[i][j]['col']], K['Kernel'][var_neg, : ][:, model[i][j]['col']], self.C, numpy.zeros((len(model[i][j]['col']), 1)), numpy.array([0]))

                        #Store the model in i-j-label
                        #將 i-j 這兩個不同類別所算出來的model結果存入model[i][j]['model']
                        model[i][j]['model'] = ssvm.train()
                        del(ssvm)

            else:
                #In here, just use A's all column because not dual form
                        #在這裡則是直接使用matrix A的全部欄位放進去運算，因為這邊不是在解dual form
                col = range(K['Kernel'].shape[1])
                for i in label_var:
                    model[i] = {}
                    for j in label_var[numpy.where(label_var == i)[0] + 1 : label_var.shape[0]]:
                        model[i][j] = {}
                        var_pos = [y for y, x in enumerate(self.rlabel[self.setIndex['fold'][ith]['train']]) if x == i]
                        var_neg = [y for y, x in enumerate(self.rlabel[self.setIndex['fold'][ith]['train']]) if x == j]
                        model[i][j]['col'] = col

                        ssvm = SSVM.SSVM(K['Kernel'][var_pos, : ], K['Kernel'][var_neg, : ], self.C, numpy.zeros((len(col), 1)), numpy.array([0]))
                        #Store the model in i-j-label
                        #將 i-j 這兩個不同類別所算出來的model結果存入model[i][j]['model']
                        model[i][j]['model'] = ssvm.train()
                        del(ssvm)

        #Here is "One-Against-Rest"
        #這邊是做 "One-Against-Rest"
        elif self.strategy == 1:
            for var in label_var:
                var_pos = [i for i, x in enumerate(self.rlabel[self.setIndex['fold'][ith]['train']]) if x == var]
                var_rest = [i for i, x in enumerate(self.rlabel[self.setIndex['fold'][ith]['train']]) if x != var]
                ssvm = SSVM.SSVM(K['Kernel'][var_pos, : ], K['Kernel'][var_rest, : ], self.C, numpy.zeros((K['Kernel'].shape[1], 1)), numpy.array([0]))
                model[var] = ssvm.train()
                del(ssvm)

        else:
            print "\n===Error in trainer-multiClassifier : self.strategy must equal to 0 or 1==="
            return False
        return model

###############################################################################

#Input:
#ith = 
#testIndex = 
#Output:

#-------------------------------------------------------------------------------


#"""
###############################################################################
    def multiPredictor(self,ith,testIndex):

        #Get unique label from reduced label set
        #從reduced set中找出有哪些label
        label_var = numpy.unique(self.rlabel)

        #Build kernel matrix for ith reduced dataset
        #為ith reduced set建置出kernel matrix
        K = kernel.buildKernel(self.kernelType, self.gamma, self.rdata[testIndex,: ], self.rdata[self.setIndex['fold'][ith]['train'], : ])

        #Here is "One-Against-One"
        #這邊是做 "One-Against-One"
        if self.strategy == 0:
            result = numpy.zeros((len(testIndex), label_var.size + 1))
            for i in label_var:
                for j in label_var[numpy.where(label_var == i)[0] + 1 : label_var.shape[0]]:
                    temp = numpy.dot(K['Kernel'][:, self.model[ith][i][j]['col']], self.model[ith][i][j]['model']['w'])-self.model[ith][i][j]['model']['b']

                    for k in range(len(testIndex)):
                        if temp[k] >= 0:
                            result[k, numpy.where(label_var == i)[0]] = result[k, numpy.where(label_var == i)[0]] + 1
                        else:
                            result[k, numpy.where(label_var == j)[0]] = result[k, numpy.where(label_var == j)[0]] + 1

            for i in range(len(testIndex)):
                result[i, label_var.size] = label_var[numpy.where(result[i, : ] == max(result[i, : ]))[0][0]]
            result = result[:, label_var.size].reshape(len(testIndex), 1)

        #Here is "One-Against-Rest"
        #這邊是做 "One-Against-Rest"
        elif self.strategy == 1:
            result = numpy.zeros((len(testIndex), 1))
            value = numpy.zeros((len(testIndex), 1))
            for var in label_var:
                 temp = numpy.dot(K['Kernel'], self.model[ith][var]['w'] ) - self.model[ith][var]['b']
                 result[temp > value] = var

        else:
            print "\n===Error in trainer-multiPredictor : self.strategy must equal to 0 or 1==="
            return False
        return result

###############################################################################

#Check the result of test
#Input:
#testIndex = test data's index, use this to find the true label
#test = dataset be predicted by SSVM
#Output:
#return = "absolute error value"

#-------------------------------------------------------------------------------

#比對test的分類結果
#輸入：
#testIndex = test的index用此去找實際的label值
#test = 由SSVM預測出來的結果
#輸出：
#return = "absolute error value"
 
###############################################################################
    def errorEstimate(self, comp_index, test_label):
        compLabel = self.rlabel[comp_index]
        result = test_label == compLabel
        ErrV = 0
        for i in result:
            if i == False:
                ErrV = ErrV + 1
        return float(ErrV) / compLabel.shape[0]


    def getReduce(self, params):
        if params == 1:
            return self.setIndex['subset']
        elif params == 2:
            return [self.rdata, self.rlabel]
        else:
            pass

    def getCross(self, params, num_fold):
        pass

    def getKernel(self):
        pass

    def save(self, fname='model'):
        if self.numFold == 1 and self.handler == True:
            output={}
            output["wb"] = self.model[0]
            output["C"] = self.C
            output["gamma"] = self.gamma
            output["kernelType"] = self.kernelType
            output["strategy"] = self.strategy
            output["label_var"] = numpy.unique(self.rlabel)

            try:
                fout = open(fname + '.pkl', 'wb')
                cPickle.dump(self.rdata, fout)
                cPickle.dump(output, fout)
                fout.close()
                return True
            except:
                print "\n===Error in trainer-save : can't save model, maybe need to check file name==="
                return False
        else:
            print "\n===Error in trainer-save : model can't use multi-fold==="
            return False

    def close(self):
        try:
            os.remove(self.rawData)
            os.remove(self.tempLabel)
            os.remove(self.tempData)
        except:
            print "\n===Error in trainer-close : can't remove tempData and tempLabel==="
            return False
        del(self.rlabel)
        del(self.rdata)
        del(self.setIndex)
        del(self.model)



########################################Test Area########################################
"""
data=array([
[2,3,4,0],
[4,2,4,1],
[3,4,6,1],
[45,6,2,0],
[1,4,6,0],
[3,5,7,1],
[4,62,1,2],
[3,4,6,2],
[4,6,2,2]])

csv_file = open( "file.csv", 'rb' )
data = loadtxt( csv_file, delimiter = ',')
trainer=SSVMTrainer(data,34,v=5,r=1)
trainer.initialize()
trainer.setting(c=100,g=0.1,t=0)
trainer.start(0)
#print trainer.model
"""
