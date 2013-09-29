
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
import scipy.stats as stats
from math import factorial


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
        
        x0, y0, treatCount = self.dataObject.getVarLists() # This should ideally be converted into a call for an object instead of individual objects.
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

    def standardError(self):
        '''Returns the standard error of the estimated ATE'''

        x0, y0, treatCount = self.dataObject.getVarLists()
        ATE = self.ATE()

        Y0 = []
        Y1 = []
        
        for value in x0:
            if value == "?":
                pass
            else:
                Y0.append(value)

        for value in y0:
            if value == "?":
                pass
            else:
                Y1.append(value)

        n = len(Y0)+len(Y1)
        m = len(Y1)

        return np.sqrt((np.var(Y0, ddof=-1, dtype=np.float64)/(n-m))+(np.var(Y1, ddof=-1, dtype=np.float64)/m))

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

        yNull = copy.deepcopy(xNull) 
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
        perms=(factorial(len(x0))/(factorial(treatCount)*factorial(len(x0)-treatCount)))

        
        random.seed(randomSeed)
        start = random.randint(0, (perms/4))
        permSteps=[]
        for trial in range(numTrials):
            permSteps.append(random.randint(0, numTrials*100))

        for n in permSteps:
            xTest =[]
            yTest=[]
            wereTreatedList = []

            for q in range(n):
                iterObject.next()

            treat = tuple(iterObject.next())
            print treat

            # need to request itam from iterable here
            
            for treatStep in treat:
                yTest.append(yNull[treatStep])
                wereTreatedList.append(treatStep)

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
            self.ATEList = self.inferenceObject.simulateAllPermutations()
        else:
            self.ATEList = self.inferenceObject.simulateTrials(numTrials, randomSeed)
        self.ATE = self.inferenceObject.ATE()
        self.x0, self.y0, self.treatCount = self.dataObject.getVarLists()
        self.ATEList.sort()

    def simplePValue(self, tails=1):
        '''Performs a simple calculation of the p value for the null hypothesis based on pg. 62  Tails can equal 1 or 2'''
        
        randomizations = len(self.ATEList)
        upper = 0.0
        lower = 0.0
        if tails==1:
            for score in self.ATEList:
                if score >= self.ATE:
                    upper += 1
                else:
                    lower += 1
            return upper/randomizations

        elif tails==2:
            for score in self.ATEList:
                if abs(score) >= self.ATE:
                    upper += 1
                else:
                    lower += 1
            return upper/randomizations
            

    def confidenceInterval(self, tails=1, alpha=0.05):
        '''Returns either a value or a list of 2 values for confidence interval (really bad I know)'''

        randomizations = len(self.ATEList)
        if tails==1:
            print(int(randomizations*(1-alpha)))
            n = self.ATEList[int(randomizations*(1-alpha))-1]
            return n
        elif tails==2:
            nlow = self.ATEList[int(randomizations*(alpha/2))-1]
            nhigh = self.ATEList[int(randomizations*(1-(alpha/2)))-1]
            return[nlow,nhigh]
                  

    def plot(self, tails=1, alpha=0.05):
        '''Simple plot to show randomizations, ATE, confidence intervals'''
        fig = plt.figure()
        ax1 = fig.add_subplot(111)

        x = range(len(self.ATEList))
        y = self.ATEList

        ax1.scatter(x,y,color='blue',marker="o",edgecolor='none')
        ax1.axhline(self.ATE, color = "r", lw=2, label=("ATE="+str(self.ATE)))
        if tails==1:
            ax1.axhline(self.confidenceInterval(tails, alpha), color = "g", lw=2, label=("confidenceinterval="+str(self.confidenceInterval(tails, alpha))))
        elif tails ==2:
            ax1.axhline(self.confidenceInterval(tails, alpha)[0], color = "g", lw=2, label=("confidenceinterval="+str(self.confidenceInterval(tails, alpha)[0])))
            ax1.axhline(self.confidenceInterval(tails, alpha)[1], color = "g", lw=2, label=("confidenceinterval="+str(self.confidenceInterval(tails, alpha)[1])))
            
        ax1.grid(True)
        ax1.legend(loc="upper left")
        
        ax1.set_aspect(1./ax1.get_data_ratio())
        plt.show()

    

        
        
            









