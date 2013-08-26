from math import log
import operator
from drawtree import createPlot

def createDataSet():
    dataSet = [[1, 1, 'yes'],
	       [1, 1, 'yes'],
               [1, 1, 'maybe'],
               [0, 1, 'no'],
               [1, 0, 'no'],
               [1, 0, 'no']]
    labels = ['flippers','no surfacing','head']
    #change to discrete values
    return dataSet, labels

def retrieveTree(i):
    listOfTrees =[{'no surfacing': {0: 'no', 1: {'flippers':
	{0: 'no', 1: 'yes'}}}},
	{'no surfacing': {0: 'no', 1: {'flippers': {0: {'head': {0: 'no', 1: 'yes'}}, 1: 'no'}}}}]
    return listOfTrees[i]

#Function to calculate the Shannon entropy of a dataset.The higher the entropy, the more mixed up the data is
def calcShannonEnt(dataSet):
    numEntries = len(dataSet)
    labelCounts = {}
    #Create dictionary of all possible classes
    for featVec in dataSet:
        currentLabel = featVec[-1]
        if currentLabel not in labelCounts.keys(): labelCounts[currentLabel] = 0
        labelCounts[currentLabel] += 1
    #print(labelCounts)
    shannonEnt = 0.0
    for key in labelCounts:
        prob = float(labelCounts[key])/numEntries
        shannonEnt -= prob * log(prob,2)
    return shannonEnt
#split the dataset
def splitDataSet(dataSet, axis, value):
    retDataSet = []
    for featVec in dataSet:
        if featVec[axis] == value:
            reducedFeatVec = featVec[:axis]     #chop out axis used for splitting
            reducedFeatVec.extend(featVec[axis+1:])
            retDataSet.append(reducedFeatVec)
    return retDataSet

def chooseBestFeatureToSplit(dataSet):
    numFeatures = len(dataSet[0]) - 1      #the last column is used for the labels
    baseEntropy = calcShannonEnt(dataSet)
    bestInfoGain = 0.0; bestFeature = -1
    for i in range(numFeatures):        #iterate over all the features
        featList = [example[i] for example in dataSet]	#create a list of all the examples of this feature
        uniqueVals = set(featList)       #get a set of unique values
        newEntropy = 0.0
        for value in uniqueVals:
            subDataSet = splitDataSet(dataSet, i, value)
            prob = len(subDataSet)/float(len(dataSet))
            newEntropy += prob * calcShannonEnt(subDataSet)     
        infoGain = baseEntropy - newEntropy     #calculate the info gain; ie reduction in entropy
        if (infoGain > bestInfoGain):       #compare this to the best gain so far
            bestInfoGain = infoGain         #if better than current best, set to best
            bestFeature = i
    return bestFeature                      #returns an integer
#find majority in a class
def majorityCnt(classList):
    classCount={}
    for vote in classList:
        if vote not in classCount.keys(): classCount[vote] = 0
        classCount[vote] += 1
    sortedClassCount = sorted(classCount.iteritems(), key=operator.itemgetter(1), reverse=True)
    return sortedClassCount[0][0]

def createTree(dataSet,labels):
    classList = [example[-1] for example in dataSet]
    if classList.count(classList[0]) == len(classList): 
        return classList[0]#stop splitting when all of the classes are equal(only have classList[0])
    if len(dataSet[0]) == 1: #stop splitting when there are no more features in dataSet(just leave a label in set)
        return majorityCnt(classList)
    bestFeat = chooseBestFeatureToSplit(dataSet)
    bestFeatLabel = labels[bestFeat]
    myTree = {bestFeatLabel:{}}
    del(labels[bestFeat])
    featValues = [example[bestFeat] for example in dataSet]
    uniqueVals = set(featValues)
    for value in uniqueVals:
        subLabels = labels[:]       #copy all of labels, so trees don't mess up existing labels
        myTree[bestFeatLabel][value] = createTree(splitDataSet(dataSet, bestFeat, value),subLabels)
    return myTree   

def storeTree(inputTree,filename):
    import pickle
    fw = open(filename,'w')
    pickle.dump(inputTree,fw)
    fw.close()
    
def grabTree(filename):
    import pickle
    fr = open(filename)
    return pickle.load(fr)     

def classifyLenses():
    fr=open('lenses.txt')
    lenses=[inst.strip().split('\t') for inst in fr.readlines()]      #two-dimination array
    lensesLabels=['age', 'prescript', 'astigmatic', 'tearRate']
    lensesTree = createTree(lenses,lensesLabels) 
    createPlot(lensesTree)             

'''
myDat,labels=createDataSet()
print(myDat)
print(calcShannonEnt(myDat))
print(splitDataSet(myDat,0,1))
print(splitDataSet(myDat,0,0))
print(chooseBestFeatureToSplit(myDat))
print(createTree(myDat,labels))
myTree=retrieveTree(1)
storeTree(myTree,'class.txt')
print(grabTree('class.txt'))
createPlot(myTree)
classifyLenses()
'''

