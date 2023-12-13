from time import process_time
from collections import Counter

import env
from logs.logger import Log
from preprocessing.cleaning import Cleaning
from .info import *
from .visual import *

class Document :
    def __init__( self, documentName, SOURCE = env.SOURCE, TARGET = env.DESTINATION ):
        try:
            if documentName == '':
                raise Exception('Invalid File Name')
            
            self.name = documentName
            self.source = SOURCE
            self.processed = TARGET
            self.cleansed = False
            self.vocabulary = ""
            self.freqMap = Counter()

        except Exception as E:
            Log("", 'e', str(E))
    
    '''
        Cleans the document from stopwords, 
        applies stemming. If reset is not passed true,
        returns the last cleansed version.
    '''
    def cleanDocument( self, reset = False, performStemming = True, performStopWordRemoval=True ):
        try :
            if ( self.cleansed and reset is False ):
                return Success(True,lazy = True)
            else :
                startTime = process_time()
                
                cleaner = Cleaning(source = self.source, destination=self.processed )
                status = cleaner.cleanFile(self.name, performStemming=performStemming, performStopWordRemoval=performStopWordRemoval )
                
                self.updateVocab(reset=reset)
                self.updateFreqMap(reset=reset)
                totalTime = process_time() - startTime
                
                if ( status.message == Response.def_Success_Message ):
                    self.cleansed = True
                    return Success(True,time=totalTime)
                else :
                    return Failure(True,time=totalTime)
        except Exception as E :
            Log("", message=f"Could not clean the Document :{str(E)}", code='e')
            return Failure(False)
    
    '''
        Updates The Vocabulary of the Document
        from the source document.
    '''
    def updateVocab( self, reset = False ):
        try :
            if ( self.vocabulary == "" or reset is True):
                startTime = process_time()
                documentVocab = ""
                
                with open(self.processed + "/" + self.name) as f:
                    for line in f.readlines() :
                        documentVocab += line
                self.vocabulary = documentVocab
                
                totalTime = process_time() - startTime
                
                return Success(True, time=totalTime)
            return Success(lazy=True)
        except Exception as E :
            Log('', message=f"Could not Update the vocabulary for {self.name} : {str(E)}", code='e')
            return Failure(False)
    
    '''
        Updates the Frequency Map of the Document,
        from the source. 
    '''
    def updateFreqMap( self, reset = False):
        try :
            if ( reset is False and self.freqMap != Counter() ):
                return Success(lazy=True)
            
            startTime = process_time()
            
            self.updateVocab(reset = reset)
            self.freqMap = Counter(self.vocabulary.split('\n'))
            self.freqMap.pop("")
            totalTime = process_time() - startTime
            
            return Success(True, time=totalTime)
        except Exception as E :
            Log('', message=f"Could not Update the Frequency Set for {self.name} : {str(E)}", code='e')
            return Failure(False)
    
    '''
        Creates Custom TagCloud, using the 
        WordCloud package.
    '''
    def displayWordCloud( self, reset = False, MASK = "", BG_COLOR = "", maxWords = 50 ):
        try :
            startTime = process_time()
            
            self.updateVocab(reset)
            self.tagCloud = TagCloud(self.vocabulary)
            self.tagCloud.createTagCloud(MASK, reset=reset,BG_COLOR=BG_COLOR, maxWords=maxWords)

            totalTime = process_time() - startTime
            
            return Success(True, time=totalTime)
        except Exception as E :
            Log("", message=f"Could Not Plot the world cloud for {self.name} : {str(E)}", code = 'e')
            return Failure(False)
    
    '''
        Creates Frequency plot based on the 
        Frequency map of the document.
    '''
    def plotFrequencies( self, reset = False, LIMIT = 20, sizeX = 12, sizeY = 8, BarColor = 'blue' ):
        try :
            if ( reset is False and hasattr(self, 'barGraph') ):
                self.barGraph.displayPlot()
                return Success(lazy=True)
            
            startTime = process_time()
            
            self.updateFreqMap()
            self.barGraph = Plot( map=self.freqMap, FILENAME=self.name,limit=LIMIT, size=(sizeX, sizeY), BarColor=BarColor)
            self.barGraph.displayPlot()

            totalTime = process_time() - startTime

            return Success(True, time=totalTime)
        except Exception as E :
            Log("", message=f"Could Not Plot the world Frequency for {self.name} : {str(E)}", code = 'e')
            return Failure(False)

