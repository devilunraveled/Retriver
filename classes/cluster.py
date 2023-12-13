from collections import Counter
import math
from time import process_time

import numpy
from pandas import DataFrame
from similarityMeasure import Comparator

from .query import Query

from .info import *
import env

from .visual import TagCloud, Plot
from .document import Document
from logs.logger import *

class Cluster :
    def __init__( self, CLUSTER_NAME= "Cluster", DocumentList = [], SOURCE = env.SOURCE, DESTINATION = env.DESTINATION ):
        self.name = CLUSTER_NAME
        self.documentNameList = DocumentList
        self.size = len(DocumentList)
        self.documentList = []
        self.documentMap = {}
        self.source = SOURCE
        self.destination = DESTINATION
        self.vocabulary = ""
        self.freqMap = Counter()
        self.documentFrequency = {}
        self.termScores = {}
        self.scoringFunction = {}
        self.relevanceProbabilty = {}
        self.irrelevanceProbabilty = {}
        self.termProbabilityScore = {}

        self.__instantiated__ = False
        self.__cleaned__ = False
        self.__vocab__ = False
        self.__freqMap__ = False
        self.__df__ = False
        self.__scores__ = False
        self.__lastCriteria__ = False
        self.__relevance__ = False
        self.__irrelevance__ = False
        self.__probabilityScores__ = False
        self.__latentSemanticModel__ = False

    def instantiateDocuments( self ):
        try :
            startTime = process_time()
            self.documentList = []
            for documentName in self.documentNameList :
                doc1 = doc2 = Document(documentName, SOURCE=self.source, TARGET=self.destination)
                self.documentList.append( doc1 )
                self.documentMap[documentName] = doc2
            self.__instantiated__ = True
            
            totalTime = process_time() - startTime
            
            return Success(True, time=totalTime)
        except Exception as E :
            Log("", code='e', message=f"Could not create Cluster Documents : {str(E)}")
            return Failure(False, message=str(E))
    
    '''
        Performs basic preprocessing
        on the Cluster, removes stop 
        words, does stemming.
    '''
    def cleanCluster( self, reset = False, performStemming = True, performStopWordRemoval=True ):
        try :
            if ( reset is False and self.__cleaned__ is True ):
                return Success(lazy=True)
            
            startTime = process_time()
            
            self.instantiateDocuments()
            for document in self.documentList :
                document.cleanDocument(reset=reset, performStemming=performStemming, performStopWordRemoval=performStopWordRemoval)

            self.updateVocab(reset=reset)
            self.updateFreqMap(reset=reset)
            self.__cleaned__ = True

            totalTime = process_time() - startTime

            return Success(True, time=totalTime)
        except Exception as E:
            Log("", code='e', message=f"Could not create clean the Cluster : {str(E)}")
            return Failure(False, message=str(E))
    
    '''
        Updates the vocabulary of the
        cluster by giong through the vocabulary
        of all the documents.
    '''
    def updateVocab( self, reset = False):
        try :
            if ( reset is False and self.__vocab__ is True ):
                return Success(lazy=True)
            
            startTime = process_time()
            
            for document in self.documentList :
                document.updateVocab(reset=reset)
                self.vocabulary += document.vocabulary
            self.__vocab__ = True

            totalTime = process_time() - startTime

            return Success(True,time=totalTime)
        except Exception as E :
            Log("", code='e', message=f"Could not update clusterVocab : {str(E)}")
            return Failure(False, message=str(E))
    
    '''
        Updates the Frequency map
        by using the universal splitter.
    '''
    def updateFreqMap(self, reset = False):
        try:
            if ( reset is False and self.__freqMap__ is True ):
                return Success(lazy=True)

            startTime = process_time()

            self.updateVocab(reset=reset)
            self.freqMap = Counter(self.vocabulary.split(env.SEPARATOR))
            self.freqMap.pop("")
            self.__freqMap__ = True

            totalTime = process_time() - startTime
            
            return Success(True, time=totalTime)
        except Exception as E:
            Log("", code='e', message=f"Could not update clusterVocab : {str(E)}")
            return Failure(False, message=str(E))
    

    '''
        Initialize the Relevance probabilities.
    '''
    def initializeRelevanceProbabilty( self, reset = False, initialRelevanceProbabilty = 0.5 ):
        try :
            if ( reset is False and self.__relevance__ is True ):
                return Success(lazy=True)

            startTime = process_time()

            self.updateFreqMap(reset=reset)
            for term in self.freqMap :
                self.relevanceProbabilty[term] = initialRelevanceProbabilty
            self.__relevance__ = True

            totalTime = process_time() - startTime
            return Success(True, time=totalTime)
        except Exception as E :
            Log("", code='e', message=f"Could not intialize Relevance Probabilty : {str(E)}")
            return Failure(False, message=str(E))
    
    def updateRelevanceProbability(self, ranking = {}, queryTerms = Counter()):
        try :
            startTime = process_time()
            
            for term in queryTerms :
                df = 0
                for documentName in ranking :
                    for document in self.documentList:
                        if document.name == documentName :
                            if ( term in document.freqMap ) :
                                df += 1
                self.relevanceProbabilty[term] = float(df + 0.5)/(len(ranking) + 1)
            
            totalTime = process_time() - startTime
            return Success(True, time=totalTime)

        except Exception as E :
            Log("", code='e', message=f"Could not update Irrelevance Probability : {str(E)}")
            return Failure(False, message=str(E))
    
    '''
        Initialize the Irrelevance probabilities.
    '''
    def initializeIrrelevanceProbabilty( self, reset = False, initialIrrelevanceProbabilty = None ):
        try :
            if ( reset is False and self.__irrelevance__ is True ):
                return Success(lazy=True)

            startTime = process_time()
            
            self.updateDocumentFrequency(reset=reset)
            for term in self.freqMap :
                irrelevanceProbabilty = initialIrrelevanceProbabilty
                if ( initialIrrelevanceProbabilty is None ) :
                    if ( self.size == 0 ):
                        raise Exception('No document in the corpus.')
                    
                    irrelevanceProbabilty = float(self.documentFrequency[term])/self.size
                
                self.irrelevanceProbabilty[term] = irrelevanceProbabilty
    
            self.__irrelevance__ = True
            totalTime = process_time() - startTime
            return Success(True, time=totalTime)
        except Exception as E :
            Log("", code='e', message=f"Could not intialize Irrelevance Probabilty : {str(E)}")
            return Failure(False, message=str(E))
    
    def updateIrrelevanceProbability(self, ranking = {}, queryTerms = Counter() ):
        try :
            startTime = process_time()
            
            for term in queryTerms :
                df = 0
                for documentName in ranking :
                    for document in self.documentList:
                        if document.name == documentName :
                            if ( term in document.freqMap ) :
                                df += 1
                self.irrelevanceProbabilty[term] = float(self.documentFrequency[term] - df + 0.5)/(self.size - len(ranking) + 1 )
            totalTime = process_time() - startTime
            return Success(True, time = totalTime)
        except Exception as E :
            Log("", code='e', message=f"Could not update Irrelevance Probability : {str(E)}")
            return Failure(False, message=str(E))

    '''
        Displays the word cloud for the 
        given cluster, can even optionally 
        take masks as input.
    '''
    def displayWordCloud( self, reset = False, MASK = "", BG_COLOR = "", maxWords = 50 ):
        try :
            startTime = process_time()
            
            self.updateVocab(reset)
            self.tagCloud = TagCloud(self.vocabulary, FILENAME=self.name)
            self.tagCloud.createTagCloud(MASK, reset=reset,BG_COLOR=BG_COLOR, maxWords=maxWords)

            totalTime = process_time() - startTime
            
            return Success(True, time=totalTime)
        except Exception as E :
            Log("", message=f"Could Not Plot the world cloud for {self.name} : {str(E)}", code = 'e')
            return Failure(False)
    
    '''
        Creates Frequency plot based on the 
        Frequency map of the cluster.
    '''
    def plotFrequencies( self, reset = False, limit = 20, sizeX = 12, sizeY = 8, BarColor = 'lightgreen', showValues = False, Labels= ["Occurence", "Word"] ):
        try :
            if ( reset is False and hasattr(self, 'barGraph') ):
                self.barGraph.displayPlot()
                return Success(lazy=True)
            
            startTime = process_time()
            
            self.updateFreqMap(reset = reset)
            self.barGraph = Plot( map=self.freqMap, FILENAME=self.name,limit=limit, size=(sizeX,sizeY), BarColor=BarColor, Labels=Labels, showValues = showValues)
            self.barGraph.displayPlot()

            totalTime = process_time() - startTime

            return Success(True, time=totalTime)
        except Exception as E :
            Log("", message=f"Could Not Plot the world Frequency for {self.name} : {str(E)}", code = 'e')
            return Failure(False)

    '''
        Updates the Document Frequency by
        considering only the topPStems from 
        each document.
    '''
    def updateDocumentFrequency( self, reset = False, topPStems = -1 ):
        try :
            if ( reset is False and self.__df__ is True and topPStems == self.__df__p__ ):
                return Success(lazy=True)

            startTime = process_time()
            
            self.updateFreqMap(reset=reset)
            self.documentFrequency = {}
            encountered = {}

            for document in self.documentList:
                for word in document.freqMap:
                    if ( word in encountered ):
                        continue
                    encountered[word] = 1
                    if (topPStems == -1) or ( document.freqMap.most_common(topPStems)[-1][1] <= document.freqMap[word]):
                        self.documentFrequency[word] = self.documentFrequency.get(word,0) + 1
                encountered = {}

            self.documentFrequency = Counter(self.documentFrequency)
            
            self.__df__ = True
            self.__df__p__ = topPStems

            totalTime = process_time() - startTime

            return Success(True, time=totalTime)
        except Exception as E :
            Log("", message=f"Could Not Compute the Document frequency for {self.name} : {E}", code = 'e')
            return Failure(False)
    
    '''
        Plots the Document Frequency for a
        given number of terms in the entire corpus.
    '''
    def plotDocumentFrequency(self, reset = False, TITLE = "Document Ferquency Plot", LIMIT = 50, BarColor = 'Green', Labels = ["Words", "Number Of Documents"], topPStems = -1, orientation = "Vertical", showValues = False):
        try:     
            startTime = process_time()
            
            self.updateDocumentFrequency(reset=reset, topPStems = topPStems)
            idfPlot = Plot( map = Counter(self.documentFrequency), FILENAME = self.name, TITLE = TITLE,Labels=Labels, BarColor=BarColor, limit = LIMIT, orientation=orientation, showValues=showValues )
            idfPlot.displayPlot()

            totalTime = process_time() - startTime

            return Success(True,time=totalTime)
        except Exception as E:
            Log("", message=f"Could Not Plot the Document frequency for {self.name} : {E}", code = 'e')
            return Failure(False)
    
    def updateTermProbabilityScore(self, reset = False, queryDomain = None):
        try :
            if ( reset is False and self.__probabilityScores__ is True ):
                return Success(lazy=True)

            startTime = process_time()
            
            if ( not hasattr(self, 'scoringScheme') or self.scoringScheme is None ):
                self.scoringScheme = Scoring(cluster=self)
            
            hyperParams = {}
            hyperParams['relevanceProbabilty'] = self.relevanceProbabilty
            hyperParams['irrelevanceProbabilty'] = self.irrelevanceProbabilty
            self.__probabilityScores__ = True

            for term in self.freqMap:
                if ( queryDomain is not None and term not in queryDomain ):
                    continue
                self.termProbabilityScore[term] = self.scoringScheme.calculateScore(term=term,hyperParams=hyperParams, scoringCriteria='probabilisticScoring').returnValue
        
            totalTime = process_time() - startTime
            return Success(True, time=totalTime)
        except Exception as E:
            Log("", message=f"Could Not Update Term Probability Score for {self.name} : {E}", code = 'e')
            return Failure(False)

    '''
        Calculate the scores for each term, based on 
        the selected scoring criteria.
    '''
    def updateTermScores(self, reset = False, scoringCriteria = 'tfIdf' ):
        try:
            if ( reset is False and self.__scores__ is True and self.__lastCriteria__ == scoringCriteria ):
                return Success(lazy=True)

            startTime = process_time()
            
            self.updateFreqMap(reset=reset)
            self.updateDocumentFrequency(reset=reset)
            self.scoringScheme = Scoring(cluster=self)
            
            termScores = {}

            for document in self.documentList:
                termDocumentScore = 0
                documentScore = {}
                hyperParams = {}
                mostFrequentTerm = document.freqMap.most_common()[-1][1]
                hyperParams['mostFrequent'] = mostFrequentTerm
                for term in self.freqMap :
                    if ( term in document.freqMap):
                        termDocumentScore = self.scoringScheme.calculateScore(term=term, document=document, scoringCriteria=scoringCriteria,hyperParams=hyperParams).returnValue
                    else :
                        termDocumentScore = 0
                    documentScore[term] = termDocumentScore
                termScores[document.name] = documentScore

            # self.termScores = DataFrame.from_dict(termScores, orient='index')
            self.termScores = termScores
            self.__scores__ = True
            self.__lastCriteria__ = scoringCriteria

            totalTime = process_time() - startTime
            
            return Success(True,time=totalTime)
        except Exception as E:
            Log("", message=f"Could Not compute the scoring for {self.name} : {E}", code = 'e')
            return Failure(False)

    def documentRetrieval(self, reset = False, query ='Lorem ipsum dolor sit amet', scoringCriteria = 'tfIdf',documentLimit = -1, performStemming = True, performStopWordRemoval = True):
        try :
            startTime = process_time()

            self.updateTermScores(reset = reset, scoringCriteria = scoringCriteria )
            # Bit of an odd manuever innit?
            thisQuery = Query(query=query, performStemming = performStemming, performStopwordRemoval = performStopWordRemoval, cluster = self)
            thisQuery.cleanQuery()
            thisQuery.computeTermFrequency()
            
            if ( scoringCriteria == 'booleanScoring' ):
                thisQuery.computeBooleanRepresentation()
            else :
                thisQuery.computeVectorRepresentation()

            comparator = Comparator(query = thisQuery, termDocumentFrequency = self.termScores, docummentNameList = self.documentNameList)
            
            printed = 0
            if scoringCriteria != 'booleanScoring':
                for key, value in comparator.vectorComparison().items():
                    if (printed > documentLimit or value == 0):
                        break
                    print(f"{key} : {value:0,.5f}")
                    printed += 1 
            else :
                for key, value in comparator.booleanComparison().items():
                    if (printed > documentLimit or value == 0):
                        break
                    print(f"{key} : {value:0,.5f}")
                    printed += 1

            totalTime = process_time() - startTime
            return Success(True,time=totalTime)
        except Exception as E:
            Log("", message=f"Could Not retrive documents for query {query} in {self.name} : {str(E)}", code = 'e')
            return Failure(False)
    
    def binaryIndependenceModel(self, reset = False, query = "", documentLimit = 15, topR = 20, performStopWordRemoval = True, performStemming = True, numEpochs = 10, initialRelevanceProbabilty = 0.5, initialIrrelevanceProbabilty = None ):
        try :
            startTime = process_time()

            self.initializeRelevanceProbabilty(reset= reset, initialRelevanceProbabilty=initialRelevanceProbabilty)
            self.initializeIrrelevanceProbabilty(reset = reset, initialIrrelevanceProbabilty=initialIrrelevanceProbabilty)
            self.updateTermProbabilityScore(reset=True)

            thisQuery = Query(query=query, performStemming = performStemming, performStopwordRemoval = performStopWordRemoval, cluster = self)
            thisQuery.cleanQuery()
            thisQuery.computeTermFrequency()
            
            previousRanking = {}
            ranking = {}
            
            while ( numEpochs > 0 ):
                comparison = Comparator(query = thisQuery, termScores = self.termProbabilityScore, docummentNameList = self.documentNameList, documentList=self.documentList)
                previousRanking = ranking
                ranking = comparison.probabilisticScoring(topR=topR)

                self.updateRelevanceProbability( ranking, thisQuery.tf)
                self.updateIrrelevanceProbability( ranking, thisQuery.tf)
                self.updateTermProbabilityScore(reset=True, queryDomain = thisQuery.tf)
                
                numEpochs -= 1 
                if ( previousRanking.items() == ranking.items() ):
                    break
                
            printed = 0
            for key,value in ranking.items():
                if (printed > documentLimit or value <= 0):
                    break
                print(f"{key} : {value:0,.5f}")
                printed += 1

            totalTime = process_time() - startTime
            return Success(True,time=totalTime, returnObject={'ranking' : ranking})

        except Exception as E:

            Log("", message=f"Could Not retrive documents for query {query} in {self.name} : {E.with_traceback}", code = 'e')
            return Failure(False)
    

    def latentSemanticModel(self, reset = False, query = "", documentLimit = 15, topEigenValues = 80, performStopWordRemoval = True, performStemming = True):
        try :
            if ( reset is False and self.__latentSemanticModel__ is True ):
                return Success(lazy=True)
            
            startTime = process_time()
            
            self.updateTermScores(reset = reset)

            thisQuery = Query(query=query, performStemming = performStemming, performStopwordRemoval = performStopWordRemoval, cluster = self)
            thisQuery.cleanQuery()
            thisQuery.computeTermFrequency()
            thisQuery.computeVectorRepresentation()

            vectorRepresentation = thisQuery.vectorRepresentation
            termDocumentDataFrame = self.termScores
            termDocumentDataFrame['__Query'] = vectorRepresentation
            
            termDocumentDataFrame = DataFrame.from_dict(termDocumentDataFrame, orient='index')
            termDocumentMatrix = termDocumentDataFrame.T.to_numpy()
            
            #Performing SVD.
            svdTerms = numpy.linalg.svd(termDocumentMatrix)
            
            matrixU = svdTerms[0][:, :topEigenValues]
            matrixS = svdTerms[1][:topEigenValues]
            matrixVT = svdTerms[2][:topEigenValues]
            
            reducedTermDocumentMatrix = ( matrixU @ numpy.diag(matrixS) ) @ matrixVT

            finalScoringMatrix = reducedTermDocumentMatrix.T @ reducedTermDocumentMatrix
            
            scores = {}

            for ( score, document ) in zip(finalScoringMatrix[-1], self.documentList):
                scores[document.name] = score
            
            sortedScores = dict(sorted(scores.items(), key=lambda item: -item[1]))
            
            printed = 0
            for key,value in sortedScores.items():
                if (printed > documentLimit or value <= 0):
                    break
                print(f"{key} : {value:0,.5f}")
                printed += 1


            totalTime = process_time() - startTime
            return Success(True,time=totalTime, returnObject={'reducedMatrix' : reducedTermDocumentMatrix, 'scores' : sortedScores})
        except Exception as E :
            Log("", message=f"Could Not retrive documents for query {query} in {self.name} : {E.with_traceback}", code = 'e')
            return Failure(False)
'''
    A scoring class, defined with relation to a cluster, 
    since both the cluster class and scoring class are 
    dependent on each other in some way, instead of creating
    a different file altogether for Scoring, I have added it 
    as another class for cluster operations.
'''


'''
    Scoring Class, used to create ScoreScheme obejcts 
    that help in performing scoring schemes on the clusters,
    for example, tfidf, BM25 etc.
'''
class Scoring :
    def __init__(self, cluster = Cluster() ):
        self.cluster = cluster
        
    def _tfIdf(self, term = None, document = None, base = 10, hyperParams = None ):
        try:
            if term == '' or document is None:
                raise Exception('Invalid arguments passed to tfidf scoring function.')

            startTime = process_time()
            tf  = 0
            idf = 0

            if ( term in document.freqMap ):
                tf = 1 + math.log(document.freqMap[term], base)
            else :
                totalTime = process_time()
                return Success(True, time=totalTime, returnValue=0)

            totalDocs = len( self.cluster.documentList)
            idf = math.log(totalDocs/self.cluster.documentFrequency[term], base)

            totalTime = process_time() - startTime
            
            return Success(time=totalTime, returnValue = idf*tf)
        except Exception as E :
            Log("", message=f"Could Not compute tfIdf for {self.cluster.name} : {E}", code = 'e')
            return Failure(False)
    
    def _lineartfIdf(self, term = None, document = None, base = 10, hyperParams = None ):
        try :
            if term == None or term == '' or document is None or hyperParams is None :
                raise Exception('Invlid arguments passed to ifIdf')

            startTime = process_time()
            tf = 0
            idf = 0

            if term in document.freqMap :
                tf = document.freqMap[term]/hyperParams['mostFrequent']
            else :
                totalTime = process_time() - startTime
                return Success(True,time=totalTime)

            totalDocs = len(self.cluster.documentList)
            idf = math.log(totalDocs/self.cluster.documentFrequency[term], base)

            totalTime = process_time() - startTime

            return Success(True,time=totalTime,returnValue=tf*idf)
        except Exception as E:
            Log("", message=f"Could Not compute linearTfIdf for {self.cluster.name} : {E}", code = 'e')
            return Failure(False)
    
    def _booleanScoring(self, term = None, document = None, base = 10, hyperParams = None ):
        try :
            startTime = process_time()
            
            if ( term is None or document is None ):
                raise Exception('Invalid arguments passed to booleanScoring')

            present = 0

            if ( term in document.freqMap ):
                present = 1
            
            totalTime = process_time() - startTime

            return Success(True,time=totalTime, returnValue=present)
        except Exception as E:
            Log("", message=f"Could Not compute booleanScoring for {self.cluster.name} : {E}", code = 'e')
            return Failure(False)
    
    def _probabilisticScoring(self, term = None, document = None, base = 10, hyperParams = None ):
        try :
            startTime = process_time()
            
            if ( term is None or hyperParams is None ):
                raise Exception('Invalid arguments passed to probabilisticScoring')

            relevanceProbabilty = hyperParams['relevanceProbabilty'][term]
            irrelevanceProbabilty = hyperParams['irrelevanceProbabilty'][term]

            if ( relevanceProbabilty > 0 and relevanceProbabilty < 1 ):
                if ( irrelevanceProbabilty > 0 and irrelevanceProbabilty < 1 ):
                    bestGuess = math.log(1 + relevanceProbabilty/(1 - relevanceProbabilty), base) + math.log(1 + (1 - irrelevanceProbabilty)/(irrelevanceProbabilty), base)
                    totalTime = process_time() - startTime
                    return Success(True, time=totalTime, returnValue=bestGuess)
            
            return Success(True, lazy=True, returnValue=0)
        except Exception as E:
            Log("", message=f"Could Not compute probabilisticScoring for {self.cluster.name} : {E}", code = 'e')
            return Failure(False)
    
    def calculateScore(self, scoringCriteria = 'tfIdf', term = None, document = None, logBase = 10, hyperParams = None):
        try :
            startTime = process_time()

            thisFunction = getattr(self,'_' + scoringCriteria)
            score = thisFunction(term = term, document=document, base = logBase, hyperParams = hyperParams).returnValue
            
            totalTime = process_time() - startTime
            
            return Success(True, time = totalTime, returnValue=score)
        except Exception as E:
            Log("", message=f"Could Not compute {scoringCriteria} for {self.cluster.name} : {E}", code = 'e')
            return Failure(False)
