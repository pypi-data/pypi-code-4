#! /usr/bin/python
# -*- coding: utf-8 -*-


#If you have any questions, please contact any of the following:
#Evan(evan176@hotmail.com)


import sys, random,numpy

###############################################################################

#Separate data to two part:training part and testing part
#Input:
#label = label of data ,label must be numpy mx1 array
#Numfold = How fold in data want to separate,result is a "index list"
#Output:
#Kresult = train + test
#    train = training dataset
#    test = testing dataset

#-------------------------------------------------------------------------------

#在CrossValidation會將資料切割成很多份，來組成訓練資料集以及驗證資料集
#輸入：
#label = 資料的label，這裡必須要是numpy mx1 array
#Numfold = 在作CrossValidation想要分成幾份，結果是一個 "index list"
#輸出：
#result = train + test
#    train = 訓練資料集
#    test = 驗證資料集

###############################################################################
def crossValidation(label, num_fold=1):

    #Set limit on data matrix : label
        #設定矩陣 label 的限制
    if not isinstance(label, numpy.ndarray):
        print "\n===Error in crossValidation : label must be array==="
        return False

    #Set limit on parameter : Numfold
        #設定參數 Numfold 的限制
    if (not isinstance(num_fold, int)) or num_fold < 1:
        print "\n===Error in crossValidation : Numfold must be int and >= 1==="
        return False

    #Get the nuique label
        #中找出有哪些label
    label_var = numpy.unique(label)
    fold = list()
    for i in range(num_fold):
        fold.append(list())

    #Find the index in data with each label
    #找出資料中每個類別的index
    for var in label_var:
        count = 0
        for i in range(label.shape[0]):
            if label[i] == var:
                fold[count].append(i)
                count = count + 1
            if count == num_fold:
                count = 0


    #Store the separate data in every fold,and combine this data to cross folds
    #There have 'train' and 'test' set in each fold
    #將分割開來的資料存在每一個 fold裡，在將這些fold整合成cross folds\
    #每一個fold都有 '訓練資料集' '驗證資料集' 兩部份
    result=[]

    for i in fold:
        temp = []
        for j in fold:
            if i != j:
                temp = temp + j
        #i={'train':temp,'test':i}
        if num_fold == 1:
            result.append({'train': i, 'test': i}) 
        else:
            result.append({'train': temp, 'test': i})

    #result is a "index list"
    #回傳的結果是一個 "index list"
    return result

###############################################################################

#Randomly get the reduced dataset from full dataset
#Input:
#label = label in data
#ratio = How ratio want in full dataset
#Output:
#subset = reduced set's index

#-------------------------------------------------------------------------------

#從完整資料集中隨機抽樣出當作reduced set
#輸入：
#label = 資料的標籤
#ratio = 想要取多少比例的資料當作reduced set
#輸出：
#subset = reduced set 在完整資料集的index

###############################################################################
def reduceSet(label, ratio):

#label = label column in data ,label must be mx1 array,
#ratio = How big in data want to use.result is a """index list"""

    #Set limit on data matrix : label
        #設定矩陣 label 的限制
    if not isinstance(label, numpy.ndarray):
        print "\n===Error in reduceSet : label must be array==="
        return False

    #Set limit on parameter : ratio
        #設定參數 ratio 的限制
    if ratio > 1 or ratio <= 0:
        print "\n===Error in reduceSet : ratio must <= 1 and ratio > 0==="
        return False

            
    #from here to reduce data
    #從這裡開始隨機取出資料
    label_var = numpy.unique(label)
    subset=[]
    for var in label_var:
        Num = round(numpy.size(numpy.where(label == var)) * ratio, 0)
        subset = subset + random.sample(numpy.where(label == var)[0], int(Num))

    #result is a "index list"
    #回傳的結果是一個 "index list"
    return subset

###############################################################################

#Get the slice of data
#Input:
#label = class of  data
#ratio = How ratio want to sample in full dataset
#Output:
#list = subset + fold
#    subset = reduced set's index
#    fold = CrossValidation with reduced set

#-------------------------------------------------------------------------------

#Get the slice of data
#輸入：
#label = 資料的標籤
#ratio = 在完整資料集中，想要取出多少比例作reduced set
#輸出：
#return = subset + fold
#    subset = reduced set's index
#    fold = 用reduced set作CrossValidation出的set

###############################################################################
def splitData(label, ratio=1, num_fold=1):
    import sys, random, numpy
    #Set limit on data matrix : label
        #設定矩陣 label 的限制
    if not isinstance(label, numpy.ndarray):
        print "\n===Error in split_data : label must be array==="
        return False

    #Set limit on parameter : ratio
        #設定參數 ratio 的限制
    if ratio > 1 or ratio <= 0:
        print "\n===Error in splitData : ratio must <= 1==="
        return False

    #Set limit on parameter : Numfold
        #設定參數 Numfold 的限制
    if (not isinstance(num_fold, int)) or num_fold < 1:
        print "\n===Error in splitData : Numfold must be int and >= 1==="
        return False

    #Store reduced set's index in 'subset'
    #儲存reduced set的 index到 'subset'
    subset = reduceSet(label, ratio)

    #Use 'subset' to do CrossValidation
    #使用 'subset' 去作CrossValidation
    fold = crossValidation(label[subset], num_fold)    

    #return is a dictionary contain two list: 'subset', 'fold'
    #return是一個字典包含兩個list: 'subset', 'fold'
    return {'subset': subset, 'fold': fold}




########################################Test Area########################################

#a=random.random_integers(40, size=(100000,2.))
"""
a=array([[2,3],[3,4],[4,1],[3,4],[2,3],[1,4],[4,3],[2,1],[4,1],[3,1]])
start=time.time()
b=CrossValidation(a[:,1].reshape(5,2),0.5)
stop=time.time()
print stop-start
print b
"""
