from collections import Counter
from time import process_time
from matplotlib import pyplot

from wordcloud import WordCloud

from PIL import Image
import numpy as np

from logs.logger import *
from .info import *

class TagCloud :
    def __init__(self, vocabulary = "IRE", FILENAME = ""):
        try:
            self.vocabulary = vocabulary
            self.fileName = FILENAME
            self.exists = False
            self.__BG__COLOR__ = "#FFFDD0"
        except Exception as E:
            Error("", message=f"Could not initialize the plot for the Document {self.fileName} : {str(E)}")
            return Failure(False)
    
    def createTagCloud(self, MASK = "", randomMask = False, reset = False, BG_COLOR = 'grey', maxWords = 100 ):
        try:
            if ( self.exists is False and reset is False ):
                pyplot.imshow(self.wordCloud)
                pyplot.axis('off')
                pyplot.show(block=True)
                return Success(lazy=True)
            
            startTime = process_time()
            if ( BG_COLOR == "" ):
                BG_COLOR = self.__BG__COLOR__
            
            if ( MASK == "" and randomMask is False ) : # Simple Box type tag cloud.
                self.wordCloud = WordCloud(background_color=BG_COLOR, max_words = maxWords, scale=3, collocations=False, stopwords= [""] ).generate(self.vocabulary)
            else :
                maskImage = np.array(Image.open(MASK))
                self.wordCloud = WordCloud(background_color=BG_COLOR,max_words=maxWords,mask=maskImage, scale = 3, collocations=False).generate(self.vocabulary)
            
            totalTime = process_time() - startTime

            if self.wordCloud is None :
                return Failure(True, time=totalTime, message="WorldCloud Could not be synthesized.")

            pyplot.imshow(self.wordCloud, interpolation='bilinear')
            pyplot.axis('off')
            pyplot.show(block=True)

            self.exists = True
            return Success(True, time=totalTime)
        except Exception as E:
            Error("", message=f"Could not generate the Tag Cloud for the Document {self.fileName} : {str(E)}")
            return Failure(False)

class Plot :
    def __init__( self, score = {}, map = Counter(), FILENAME = "", TITLE = "Frequency Plot", limit = 20, size = (12,8), BarColor = 'grey', orientation = 'Horizontal', Labels = ["", ""], showValues = False, showLabels = True ):
        self.name = FILENAME
        self.map = map
        self.score = score
        
        self.title = TITLE
        self.limit = limit
        self.size = size
        self.BarColor = BarColor
        self.orientation = orientation
        self.Labels = Labels
        self.showValues = showValues
        self.showLabels = showLabels

    def displayPlot( self ):
        try :
            startTime = process_time()
            
            if ( self.score != {} ):
                self.map = self.score

            sortedScores = sorted(self.map.items(), key=lambda items : items[1], reverse = True )
            limitedPicks = sortedScores[:self.limit]

            terms, scores = zip(*limitedPicks)

            pyplot.figure(figsize=self.size)
            
            if ( self.orientation == 'Horizontal'):
                bars = pyplot.barh(terms, scores, color = self.BarColor)
                pyplot.gca().invert_yaxis() # type: ignore
                # Make pyright ( or your linter ) ignore the apparent redundant error.
            else :
                pyplot.xticks(rotation=90)  # Rotate x-axis labels for better readability 
                bars = pyplot.bar(terms, scores, color = self.BarColor)
            
            pyplot.xlabel(self.Labels[0])
            pyplot.ylabel(self.Labels[1])
            
            if ( self.showLabels is False or self.limit > 60):
                pyplot.gca().set_xticklabels([]) # type: ignore

            pyplot.title(self.title)
            pyplot.tight_layout()  # Ensures labels fit within the plot area
            
            if self.showValues :
                if ( self.orientation == 'Vertical') :
                    for bar, score in zip(bars, scores):
                        pyplot.text(bar.get_x() + bar.get_width() / 2 - 0.10, bar.get_height() + 0.05, f'{score:.1f}', fontsize=9, ha='center')
                else :
                    for bar, score in zip(bars, scores):
                        pyplot.text(bar.get_width() + 22, bar.get_y() + bar.get_height()/2 - 0.10 , f'{score:.1f}', fontsize=9, ha='center')

            # pyplot.savefig('FirstFifteenPlot.png', dpi=600)
            
            pyplot.show()
            totalTime = process_time() - startTime
            return Success(True, time=totalTime)
        except Exception as E:
            Error("", message=f"Could not generate the Word Frequency for the Document {self.name} : {str(E)}")
            return Failure(False)
