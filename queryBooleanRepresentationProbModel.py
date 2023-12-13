from classes.query import Query
from logs.logger import *
from main import Executor

def takeInput( ):
    query = input("Enter your query: ")
    return query

if __name__ == "__main__":
    try :
        thisExecutor = Executor(NUMFILES=-1)
        thisExecutor.initiateCluster()
        thisCluster = thisExecutor.cluster
        
        if ( thisCluster is None ):
            raise Exception('Invalid Cluster passed')
        thisCluster.instantiateDocuments()
        thisCluster.cleanCluster()
        thisCluster.updateFreqMap()

        thisQuery = Query(query=takeInput(), performStopwordRemoval=True, performStemming=True, cluster = thisCluster)
        thisQuery.cleanQuery()
        thisQuery.computeTermFrequency()
        thisQuery.computeBooleanRepresentation()

        print(thisQuery.booleanRepresentation['fadd'])
    except Exception as E:
        Log("",code='e',message=f"Could not start the execution : {str(E)}")
