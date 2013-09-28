#####
# Python 2.7.3
# Chapters 3 and 4 - Field Experiments Problems
# Random Inference functions
# Tanya Whyte
#####

import numpy as np
import matplotlib.pyplot as plt
import csv
import copy
import itertools
import random


# import the csv file of data, put into 2 lists

class readFile(object):
    def __init__(self, dataFile = "data.csv"):
        self.dataFile = dataFile
        self.data = []
        with open(self.dataFile, 'rt') as csvfile:
            spamreader = csv.DictReader(csvfile, ["x0", "y0"])
            for row in spamreader:
                if row["x0"] == "":
                    pass
                else:
                    self.data.append(row)
    def getData(self):
        return self.data

    def getVarLists(self):
        raws=self.getData()

        x0 = []
        y0 = []
        treatCount = 0
        
        for line in raws:
            if (line["x0"]) != "?":
                x0.append(float(line["x0"]))
            else:
                x0.append("?")
            if (line["y0"]) != "?":
                y0.append(float(line["y0"]))
                treatCount+=1
            else:
                y0.append("?")

        return x0, y0, treatCount

class randomInference(object):
    def __init__(self, dataFile = "data.csv"):
        self.dataFile = dataFile
        self.dataObject = readFile(self.dataFile)

    def ATE(self):
        '''Returns average treatment effect calculated from data with "?" blanks'''
        
        x0, y0, treatCount = self.dataObject.getVarLists() # This should ideally converted into a call for an object instead of individual objects.
        meanHolder=0.0
        counter = 0
        xMean=0.0
        yMean=0.0
        treatmentEffect = 0.0
        
        for value in x0:
            if value == "?":
                pass
            else:
                meanHolder += value
                counter +=1

        xMean = meanHolder/counter
        meanHolder=0.0
        counter = 0

        for value in y0:
            if value == "?":
                pass
            else:
                meanHolder += value
                counter +=1

        yMean = meanHolder/counter
        treatmentEffect = yMean-xMean
        return treatmentEffect
              

    def simulateAllPermutations(self):
        '''Iterates over all possible random permutations and returns a list of all possible ATEs.
        Make sure this is not too huge to do!'''
        
        x0, y0, treatCount = self.dataObject.getVarLists()
        treatmentEffect = self.ATE()
        print("The ATE for observed data is: " + str(treatmentEffect))
        xNull = []

        for fill in range(len(x0)):
            if x0[fill] =="?":
                xNull.append(y0[fill])
            else:
                xNull.append(x0[fill])

        yNull = copy.deepcopy(xNull) #
        iterList = list(itertools.islice(itertools.combinations((range(len(x0))), treatCount), None)) # creates a list of tuples representing all possible permutations

        # main for loop
        fullResults = []
        for perm in range(len(iterList)):
            yTest = []
            xTest = []
            wereTreatedList = []
            for treatedIndex in range(treatCount): # how many in treated group?
                yTest.append(yNull[(iterList[perm][treatedIndex])])
                wereTreatedList.append(iterList[perm][treatedIndex])
            for allIndex in range(len(xNull)):
                if allIndex in wereTreatedList:
                    pass
                else:
                    xTest.append(float(xNull[allIndex]))
            fullResults.append(np.mean(yTest) - np.mean(xTest))

        return fullResults


    def simulateTrials(self, numTrials, randomSeed=1):
        '''Iterates over numTrials randomized trials of possible permutations (must be equal or less than maximum permutations).  randomSeed defaults to 1'''
        
        x0, y0, treatCount = self.dataObject.getVarLists()
        treatmentEffect = self.ATE()
        print("The ATE for observed data is: " + str(treatmentEffect))
        xNull = []

        for fill in range(len(x0)):
            if x0[fill] =="?":
                xNull.append(y0[fill])
            else:
                xNull.append(x0[fill])

        yNull = copy.deepcopy(xNull) 
        iterObject = itertools.combinations((range(len(x0))), treatCount)

        fullResults = []
        random.seed(randomSeed)

        pool = tuple(iterObject)
        perm = tuple(random.sample(pool, numTrials))

        for trialIndex in perm:

            yTest = []
            xTest = []
            wereTreatedList = []
            
            for treat in trialIndex:
                yTest.append(yNull[treat])
                wereTreatedList.append(treat)

            for allIndex in range(len(xNull)):
                if allIndex in wereTreatedList:
                    pass
                else:
                    xTest.append(float(xNull[allIndex]))
            fullResults.append(np.mean(yTest) - np.mean(xTest))

        return fullResults
            
class hypothesisTest(object):
    def __init__(self, numTrials='all', randomSeed=1, dataFile = "data.csv"):
        '''numTrials can either be str "all" for all trials or an int'''
        self.dataFile = dataFile
        self.dataObject = readFile(self.dataFile)
        self.inferenceObject = randomInference(dataFile)
        if numTrials =='all':
            self.ATEList = inferenceObject.simulateAllPermutations()
        else:
            self.ATEList = inferenceObject.simulateTrials(numTrials, randomSeed)

    def confidenceInterval(self, tails=1, alpha=0.05):
        pass

    def plot(self, tails=1, alpha=0.05):
        pass

    

            

        
        
            









