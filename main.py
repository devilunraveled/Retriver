import math
import os
import sys

from matplotlib import pyplot
from pandas import DataFrame

import env

from classes.cluster import Cluster

sys.path.append("../..")

from logs.logger import *
from classes.info import *
from classes.document import Document

from sklearn.cluster import KMeans 

class Tasks :
    def __init__( self, FILENAME = "emt02495.txt" ):
        self.computed = False
        self.fileName = FILENAME

    def tokenization(self):
        try :
            thisDocument = Document(self.fileName)
            thisDocument.cleanDocument()
            self.tokenized = True
        except Exception as E :
            Log("",code='e',message=f"{str(E)}")
            return Failure(False)
    
    def visualizeStuff( self, maxWords = 50, plotWords = 20 ):
        try :
            thisDocument = Document(self.fileName)
            
            if ( not hasattr(self, 'tokenized') ) :
                thisDocument.cleanDocument()
            
            resp1 = thisDocument.displayWordCloud(maxWords=maxWords)
            Inform(message=f"Time taken to plot Word Cloud : {resp1.time}")
            
            resp2 = thisDocument.plotFrequencies(LIMIT=plotWords)
            Inform(message=f"Time taken to plot Frequency Map : {resp2.time}")
        except Exception as E :
            Log("",code='e',message=f"{str(E)}")
            return Failure(False)

    def executeAll(self):
        try :
            self.tokenization()
            self.visualizeStuff()
        except Exception as E:
            Log("",message=f"Could not Execute All Tasks : {str(E)}", code='e')

class ClusterTasks :
    def __init__( self, cluster, CLUSTER_NAME = "Cluster", performStopWordRemoval=True, performStemming=True, documentLimit = 15 ):
        self.computed = False
        self.clusterName = CLUSTER_NAME
        self.cluster = cluster
        self.performStopWordRemoval=performStopWordRemoval
        self.performStemming=performStemming
        self.documentLimit = documentLimit

    def tokenization(self ):
        try :
            self.cluster.instantiateDocuments()
            self.cluster.cleanCluster(performStopWordRemoval=self.performStopWordRemoval,performStemming=self.performStemming)
            self.computed = True
        except Exception as E :
            Log("",code='e',message=f"{str(E)}")
            return Failure(False)
    
    def visualizeStuff( self, maxWords = 50, plotWords = 20, displayWordCloud = True, displayDfPlot = True, displayFreqPlot = False, displayTermScores = False ):
        try:
            if displayWordCloud :
                wordCLoudStatus = self.cluster.displayWordCloud(maxWords=maxWords, reset = True)
                Inform(message=f"Time taken to create Word Cloud : {wordCLoudStatus.time:0,.2f} seconds")

            if displayFreqPlot :
                freqPlotStatus = self.cluster.plotFrequencies(LIMIT=plotWords, reset=True, showValues=True)
                Inform(message=f"Time taken to create Frequency Plot : {freqPlotStatus.time:0,.2f} seconds")

            if displayDfPlot :
                dfPlotStatus = self.cluster.plotDocumentFrequency(reset=False, topPStems = 25)
                Inform(message=f"Time taken to create Document Frequency Plot : {dfPlotStatus.time:0,.2f} seconds")

            if displayTermScores :
                termScoreStatus = self.cluster.updateTermScores(reset=True)
                Inform(message=f"Time Taken to update Term Scores : {termScoreStatus.time:0,.2f} seconds")

            # print(self.cluster.termScores)
        except Exception as E:
            Log("",code='e',message=f"{str(E)}")
            return Failure(False)

    def executeRetrieval( self, query, documentLimit = 15 ):
        try:
            if ( self.computed is False ):
                self.cluster.instantiateDocuments()
                self.cluster.cleanCluster()
                self.computed = True

            response = self.cluster.documentRetrieval(query=query, documentLimit=documentLimit, scoringCriteria='lineartfIdf', stemsPerDocument=20)
            docList = response.returnObject

            print(f"Relevant Documents for Query : `{query}` are : ")
            
            for doc in docList :
                print( doc )
            
            Inform(message=f'Time taken to perform the search query : {response.time:0,.4f} seconds')

        except Exception as E:
            Log("",code='e',message=f"{str(E)}")
            return Failure(False)

    def executeCluster(self):
        try :
            self.tokenization()
            self.visualizeStuff()
        except Exception as E:
            Log("",message=f"Could not Execute All Tasks : {str(E)}", code='e')
    
class Executor :
    def __init__(self, CORPUS = os.path.abspath("corpus/"), NUMFILES = 15, performStopWordRemoval = True, performStemming = True ):
        self.corpus = CORPUS
        self.performStopWordRemoval = performStopWordRemoval
        self.performStemming = performStemming
        self.cluster = None
        if NUMFILES == -1 :
            self.limit = math.inf
        else :
            self.limit = NUMFILES
    
    def startExecutionIndividual(self):
        try :
            for document in os.listdir(self.corpus):
                documentName = os.fsdecode(document)
                
                if self.limit == 0 :
                    break

                if ( documentName.endswith(".txt") ):
                    newTask = Tasks(FILENAME=documentName)
                    Inform(message=f"Executing File : {documentName}")
                    newTask.executeAll()

                    self.limit -= 1
        except Exception as E:
            Log("",code='e',message=f"Could not start the execution : {str(E)}")
    
    def initiateCluster(self):
        try :
            documentNameList = []
            for document in sorted(os.listdir(self.corpus)):
                documentName = os.fsdecode(document)
                
                if self.limit == 0 :
                    break

                if ( documentName.endswith(".txt") ):
                    documentNameList.append(documentName)
                    self.limit -= 1

            newCluster = Cluster(DocumentList=documentNameList)
            self.cluster = newCluster
        except Exception as E:
            Log("",code='e',message=f"Could not start the execution : {str(E)}")

    def startExecutionCluster(self):
        try :
            self.initiateCluster()
            clusterTask = ClusterTasks(self.cluster, performStopWordRemoval=self.performStopWordRemoval, performStemming=self.performStemming)
            clusterTask.executeCluster()
            # clusterTask.executeRetrieval(query = "method")
        except Exception as E:
            Log("",code='e',message=f"Could not start the execution : {str(E)}")


class Assignement1Tasks :
    def __init__( self, source = env.SOURCE, destination = env.DESTINATION ):
        self.source = source
        self.destination = destination
        self.cluster = Cluster()
        self.performedT1 = False

    def Task1(self, numDocuments = 15, performStemming = False, performStopWordRemoval = False ):
        executor = Executor(NUMFILES=numDocuments, performStopWordRemoval=performStopWordRemoval, performStemming=performStemming)
        executor.initiateCluster()

        if ( executor.cluster is None ) :
            raise Exception('Could not create cluster.')
        
        self.cluster = executor.cluster
        executor.cluster.instantiateDocuments()
        executor.cluster.cleanCluster(performStemming=performStemming, performStopWordRemoval=performStopWordRemoval)
        self.performedT1 = True

    def Task2(self, numDocuments = 15, performStemming=True, performStopWordRemoval=False, maxWords = 50 ):
        # Perform Task 1.
        if not self.performedT1 :
            self.Task1(numDocuments=numDocuments, performStemming=performStemming, performStopWordRemoval=performStopWordRemoval)
        
        self.cluster.cleanCluster(reset=True, performStemming=performStemming, performStopWordRemoval=performStopWordRemoval)
        self.cluster.displayWordCloud(maxWords=maxWords, reset=True)
        
        # Getting Plot Frequency fot the first document.
        self.cluster.documentList[0].plotFrequencies(LIMIT=20, reset=True, BarColor='lightblue')

    def Task3(self, numDocuments = -1, performStopWordRemoval = False, performStemming = False ):
        executor = Executor(NUMFILES=numDocuments, performStopWordRemoval=performStopWordRemoval, performStemming=performStemming)
        executor.initiateCluster()

        if ( executor.cluster is None ) :
            raise Exception('Could not create cluster.')

        self.cluster = executor.cluster
        executor.cluster.instantiateDocuments()
        executor.cluster.cleanCluster(performStemming=performStemming, performStopWordRemoval=performStopWordRemoval)
        
        self.cluster.plotFrequencies(Labels = ["Frequency", "Word"])

        # Extracting only the top p most frequent terms from each document.
        # for numStems in range (5, 25, 5):
        #     self.cluster.plotDocumentFrequency(topPStems=numStems, TITLE=f"Document frequency for top {numStems} words across docs.")
        
        self.cluster.plotDocumentFrequency(LIMIT = 2000, topPStems=-1, TITLE=f"Document frequency for all words across docs.")

    def Task4(self, performStopWordRemoval = False, performStemming = True):
        executor = Executor(NUMFILES=-1)
        executor.initiateCluster()

        if (executor.cluster is None):
            raise Exception('Could not create cluster.')

        self.cluster = executor.cluster
        self.cluster.instantiateDocuments()
        self.cluster.cleanCluster(performStemming=performStemming, performStopWordRemoval=performStopWordRemoval)
        
        query = input("Enter Your Complete Query : ")
        
        print('Ranking based on vector model using tfIdf Scoring :')
        self.cluster.documentRetrieval(query = query, documentLimit = 20, scoringCriteria = 'tfIdf', performStopWordRemoval=performStopWordRemoval, performStemming=performStemming)
        
        print('Ranking based on vector model using lineartfIdf Scoring :')
        self.cluster.documentRetrieval(reset = True, query = query, documentLimit = 20, scoringCriteria = 'lineartfIdf', performStopWordRemoval=performStopWordRemoval, performStemming=performStemming)

        print('Ranking based on boolean model using boolean Scoring :')
        self.cluster.documentRetrieval(reset = True, query = query, documentLimit = 20, scoringCriteria = 'booleanScoring', performStopWordRemoval=performStopWordRemoval, performStemming=performStemming)
    
    def Task5(self, performStopWordRemoval = True, performStemming = False):
        executor = Executor()
        executor.initiateCluster()

        if executor.cluster is None:
            raise Exception('Could not create cluster.')

        self.cluster = executor.cluster
        self.cluster.instantiateDocuments()
        self.cluster.cleanCluster(performStemming=performStemming, performStopWordRemoval=performStopWordRemoval)

        self.cluster.displayWordCloud(reset = True, maxWords = 50)
    
    def Task6(self, performStopWordRemoval = True, performStemming = True):
        executor = Executor(NUMFILES=-1)
        executor.initiateCluster()

        if executor.cluster is None:
            raise Exception('Could not create cluster.')

        self.cluster = executor.cluster
        self.cluster.instantiateDocuments()
        self.cluster.cleanCluster(performStemming=performStemming, performStopWordRemoval=performStopWordRemoval)

        query = input("Enter Your Complete Query : ")
        
        print('Ranking based on vector model using tfIdf Scoring :')
        self.cluster.documentRetrieval(query = query, documentLimit = 20, scoringCriteria = 'tfIdf', performStopWordRemoval=performStopWordRemoval, performStemming=performStemming)
        
        print('Ranking based on vector model using lineartfIdf Scoring :')
        self.cluster.documentRetrieval(reset = True, query = query, documentLimit = 20, scoringCriteria = 'lineartfIdf', performStopWordRemoval=performStopWordRemoval, performStemming=performStemming)

        print('Ranking based on boolean model using boolean Scoring :')
        self.cluster.documentRetrieval(reset = True, query = query, documentLimit = 20, scoringCriteria = 'booleanScoring', performStopWordRemoval=performStopWordRemoval, performStemming=performStemming)

    def Task7(self, performStopWordRemoval = True, performStemming = True):
        executor = Executor(NUMFILES=-1)
        executor.initiateCluster()

        if executor.cluster is None:
            raise Exception('Could not create cluster.')

        self.cluster = executor.cluster
        self.cluster.instantiateDocuments()
        self.cluster.cleanCluster(performStemming=performStemming, performStopWordRemoval=performStopWordRemoval)

        numClusters = int(input("Enter Number of Clusters : "))

        kmeans = KMeans(n_clusters=numClusters, random_state=37 )
        # Creating a list of list for termScores.
        
        self.cluster.updateTermScores()
        scores = self.cluster.termScores

        kmeans.fit(DataFrame.from_dict(scores, orient='index'))
        cluster_labels = kmeans.labels_

        pyplot.hist(cluster_labels, bins=numClusters, alpha=0.5, color='orange', edgecolor='black')
        pyplot.xlabel('Cluster')
        pyplot.ylabel('Number of Documents')
        pyplot.title('Document Distribution in Clusters')

        pyplot.show()


class Assignement2Tasks :
    def __init__( self, source = env.SOURCE, destination = env.DESTINATION ):
        self.source = source
        self.destination = destination
        self.cluster = Cluster()
        self.performedT1 = False

    def Task1(self, numDocuments = 15, performStemming = False, performStopWordRemoval = False ):
        executor = Executor(NUMFILES=numDocuments, performStopWordRemoval=performStopWordRemoval, performStemming=performStemming)
        executor.initiateCluster()

        if ( executor.cluster is None ) :
            raise Exception('Could not create cluster.')
        
        self.cluster = executor.cluster
        executor.cluster.instantiateDocuments()
        executor.cluster.cleanCluster(performStemming=performStemming, performStopWordRemoval=performStopWordRemoval)
        self.performedT1 = True

    def Task2(self, numDocuments = 15, performStemming=True, performStopWordRemoval=False ):
        # Perform Task 1.
        if not self.performedT1 :
            self.Task1(numDocuments=numDocuments, performStemming=performStemming, performStopWordRemoval=performStopWordRemoval)
        
        self.cluster.cleanCluster(reset=True, performStemming=performStemming, performStopWordRemoval=performStopWordRemoval)



    def Task3(self, numDocuments = -1, performStemming = True ):
        executor = Executor(NUMFILES=numDocuments, performStopWordRemoval=False, performStemming=performStemming)
        executor.initiateCluster()

        if ( executor.cluster is None ) :
            raise Exception('Could not create cluster.')

        self.cluster = executor.cluster

        self.cluster.cleanCluster(performStemming=performStemming, performStopWordRemoval=False)
        self.cluster.plotFrequencies(Labels = ["Frequency", "Word"])

        self.cluster.cleanCluster(reset = True, performStemming=performStemming, performStopWordRemoval=True)
        self.cluster.plotFrequencies(reset = True, Labels = ["Frequency", "Word"])

    def Task4(self, performStopWordRemoval = True, performStemming = True):
        executor = Executor(NUMFILES=-1)
        executor.initiateCluster()

        if (executor.cluster is None):
            raise Exception('Could not create cluster.')

        self.cluster = executor.cluster
        self.cluster.instantiateDocuments()
        self.cluster.cleanCluster(performStemming=performStemming, performStopWordRemoval=performStopWordRemoval)
        
        query = input("Enter Your Complete Query : ")
        
        print('Ranking based on vector model using tfIdf Scoring :')
        self.cluster.documentRetrieval(query = query, documentLimit = 20, scoringCriteria = 'tfIdf', performStopWordRemoval=performStopWordRemoval, performStemming=performStemming)

        print('Ranking based on vector model using lineartfIdf Scoring :')
        self.cluster.documentRetrieval(reset = True, query = query, documentLimit = 20, scoringCriteria = 'lineartfIdf', performStopWordRemoval=performStopWordRemoval, performStemming=performStemming)

        print('Ranking based on boolean model using boolean Scoring :')
        self.cluster.documentRetrieval(reset = True, query = query, documentLimit = 20, scoringCriteria = 'booleanScoring', performStopWordRemoval=performStopWordRemoval, performStemming=performStemming)

        print('Ranking based on vector model using BIM :')
        self.cluster.binaryIndependenceModel(query = query, topR = 20, performStopWordRemoval=performStopWordRemoval, performStemming=performStemming)

        print('Ranking based on vector model using Latent Semantic Model:')
        self.cluster.latentSemanticModel(reset = True, query = query, topEigenValues = 60, performStopWordRemoval=performStopWordRemoval, performStemming=performStemming)
    
    def Task5(self, performStopWordRemoval = True, performStemming = False):
        executor = Executor()
        executor.initiateCluster()

        if executor.cluster is None:
            raise Exception('Could not create cluster.')

        self.cluster = executor.cluster
        self.cluster.instantiateDocuments()
        self.cluster.cleanCluster(performStemming=performStemming, performStopWordRemoval=performStopWordRemoval)

        self.cluster.displayWordCloud(reset = True, maxWords = 50)
    
    def Task6(self, performStopWordRemoval = True, performStemming = True):
        executor = Executor(NUMFILES=-1)
        executor.initiateCluster()

        if executor.cluster is None:
            raise Exception('Could not create cluster.')

        self.cluster = executor.cluster
        self.cluster.instantiateDocuments()
        self.cluster.cleanCluster(performStemming=performStemming, performStopWordRemoval=performStopWordRemoval)

        query = input("Enter Your Complete Query : ")
        
        print('Ranking based on vector model using tfIdf Scoring :')
        self.cluster.documentRetrieval(query = query, documentLimit = 20, scoringCriteria = 'tfIdf', performStopWordRemoval=performStopWordRemoval, performStemming=performStemming)
        
        print('Ranking based on vector model using lineartfIdf Scoring :')
        self.cluster.documentRetrieval(reset = True, query = query, documentLimit = 20, scoringCriteria = 'lineartfIdf', performStopWordRemoval=performStopWordRemoval, performStemming=performStemming)

        print('Ranking based on boolean model using boolean Scoring :')
        self.cluster.documentRetrieval(reset = True, query = query, documentLimit = 20, scoringCriteria = 'booleanScoring', performStopWordRemoval=performStopWordRemoval, performStemming=performStemming)

    def Task7(self, performStopWordRemoval = True, performStemming = True):
        executor = Executor(NUMFILES=-1)
        executor.initiateCluster()

        if executor.cluster is None:
            raise Exception('Could not create cluster.')

        self.cluster = executor.cluster
        self.cluster.instantiateDocuments()
        self.cluster.cleanCluster(performStemming=performStemming, performStopWordRemoval=performStopWordRemoval)

        numClusters = int(input("Enter Number of Clusters : "))

        kmeans = KMeans(n_clusters=numClusters, random_state=37 )
        # Creating a list of list for termScores.
        
        self.cluster.updateTermScores()
        scores = self.cluster.termScores

        kmeans.fit(DataFrame.from_dict(scores, orient='index'))
        cluster_labels = kmeans.labels_

        pyplot.hist(cluster_labels, bins=numClusters, alpha=0.5, color='orange', edgecolor='black')
        pyplot.xlabel('Cluster')
        pyplot.ylabel('Number of Documents')
        pyplot.title('Document Distribution in Clusters')

        pyplot.show()
if __name__ == "__main__":
    tasks = Assignement2Tasks()
    # tasks.Task1()
    # tasks.Task2()
    # tasks.Task3()
    tasks.Task4()
    # tasks.Task5()
    # tasks.Task6()
    # tasks.Task7()
