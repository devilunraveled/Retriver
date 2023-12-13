from PIL.Image import DecompressionBombWarning
from logs.logger import *
from classes.info import *

class Comparator:
    def __init__(self, query = None, termScores = None ,termDocumentFrequency = None, docummentNameList = None, documentList = None):
        self.query = query
        self.termScores = termScores
        self.termDocumentFrequency = termDocumentFrequency
        self.documentList = docummentNameList
        self.documentObjects = documentList

    def vectorComparison (self):
        if ( self.query is None ):
            raise Exception('Invalid Query passed')
        if ( self.documentList is None ):
            raise Exception('Invalid Document passed')
        if ( self.termDocumentFrequency is None ):
            raise Exception('Invalid Term Document Frequency passed')
        
        queryMod = 0
        for term in self.query.vectorRepresentation :
            queryMod += self.query.vectorRepresentation[term] ** 2
        queryMod = queryMod ** 0.5
        
        documentNormalizer = {}
        for document in self.documentList :
            documentMod = 0
            for term in self.termDocumentFrequency[document]:
                documentMod += self.termDocumentFrequency[document][term] ** 2
            documentMod = documentMod ** 0.5
            documentNormalizer[document] = documentMod

        score = {}

        for document in self.documentList :
            for term in self.termDocumentFrequency[document]:
                score[document] = score.get(document, 0) + self.query.vectorRepresentation[term]*self.termDocumentFrequency[document][term]
        
        for document in self.documentList :
            score[document] = score[document]/(queryMod*documentNormalizer[document])

        score = dict(sorted(score.items(), key=lambda item: -item[1]))

        return score

    def booleanComparison(self):
        if ( self.query is None ):
            raise Exception('Invalid Query passed')
        if ( self.documentList is None ):
            raise Exception('Invalid Document passed')
        if ( self.termDocumentFrequency is None ):
            raise Exception('Invalid Term Document Frequency passed')
        
        queryMod = 0
        for term in self.query.booleanRepresentation :
            queryMod += self.query.booleanRepresentation[term] ** 2
        queryMod = queryMod ** 0.5
        
        documentNormalizer = {}
        for document in self.documentList :
            documentMod = 0
            for term in self.termDocumentFrequency[document]:
                documentMod += self.termDocumentFrequency[document][term] ** 2
            documentMod = documentMod ** 0.5
            documentNormalizer[document] = documentMod

        score = {}
        
        for document in self.documentList :
            for term in self.termDocumentFrequency[document]:
                score[document] = score.get(document, 0) + self.query.booleanRepresentation[term]*self.termDocumentFrequency[document][term]
        
        for document in self.documentList :
            score[document] = score[document]/(queryMod*documentNormalizer[document])
        
        score = dict(sorted(score.items(), key=lambda item: -item[1]))
        
        return score

    def probabilisticScoring(self, topR):
        if ( self.query is None ):
            raise Exception('Invalid Query passed')
        if ( self.documentList is None ):
            raise Exception('Invalid Document passed')
        if ( self.termScores is None ):
            raise Exception('Invalid Term Scores passed')
        if ( self.documentObjects is None):
            raise Exception('Invalid Document Objects passed')
        score = {}
        
        for document in self.documentObjects :
            for term in self.query.tf :
                if (term in document.freqMap):
                    score[document.name] = score.get(document.name, 0) + self.termScores.get(term, 0)
                
        score = dict(sorted(score.items(), key=lambda item: -item[1])[:topR])

        return score
