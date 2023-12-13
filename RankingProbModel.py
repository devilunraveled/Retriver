from main import Executor
from logs.logger import *

if __name__ == "__main__":
    try :
        thisExecutor = Executor(NUMFILES=-1)
        thisExecutor.initiateCluster()

        thisCluster = thisExecutor.cluster
        
        documentLimit = int(input("Enter the limit to the search query results : "))
        query = input("Enter the query : ")

        if ( thisCluster == None ):
            raise Exception('Could not create cluster')

        thisCluster.instantiateDocuments()
        thisCluster.cleanCluster()
        
        returnedObject = thisCluster.binaryIndependenceModel(query=query, reset = True, documentLimit = documentLimit)

        if ( returnedObject is None or returnedObject.returnObject is None ):
            raise Exception('Could not perform BIM scoring')

        ranking = returnedObject.returnObject['ranking']
    except Exception as E:
        Log("", code='e', message=f"Could not create clean the Cluster : {str(E)}")
