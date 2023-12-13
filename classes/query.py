from collections import Counter
import env
from preprocessing.cleaning import Cleaning
from logs.logger import Log

from .info import *


class Query :
    def __init__(self, query = "", performStopwordRemoval = True, performStemming = True, cluster = None):
        self.query = query
        self.performStopwordRemoval = performStopwordRemoval
        self.performStemming = performStemming
        self.tf = Counter()
        self.cluster = cluster
        self.booleanRepresentation = {}
        self.vectorRepresentation = {}

    def cleanQuery(self):
        try :
            cleaner = Cleaning(self.query)
            cleaner.cleanQuery(performStopWordRemoval=self.performStopwordRemoval, performStemming=self.performStemming, query=self.query)
            self.query = cleaner.finalQuery
        except Exception as E:
            Log("", message=f"Could not clean the Query :{str(E)}", code='e')
            return Failure(False)

    def computeTermFrequency(self):
        try :
            self.tf = Counter(self.query.split(env.SEPARATOR))
            self.tf.pop('')
        except Exception as E:
            Log("", message=f"Could not compute Term Frequency :{str(E)}", code='e')
            return Failure(False)
    
    def computeBooleanRepresentation(self):
        try:
            if self.cluster is None :
                raise Exception('Invalid Cluster passed')

            for term in self.cluster.freqMap:
                if term in self.tf:
                    self.booleanRepresentation[term] = 1
                else :
                    self.booleanRepresentation[term] = 0
            
        except Exception as E:
            Log("", message=f"Could not compute Boolean Representation :{str(E)}", code='e')
            return Failure(False)

    def computeVectorRepresentation(self):
        try:
            if self.cluster is None :
                raise Exception('Invalid Cluster passed')

            for term in self.cluster.freqMap:
                if term in self.tf:
                    self.vectorRepresentation[term] = self.tf[term]
                else :
                    self.vectorRepresentation[term] = 0
        except Exception as E:
            Log("", message=f"Could not compute Vector Representation :{str(E)}", code='e')
            return Failure(False)
