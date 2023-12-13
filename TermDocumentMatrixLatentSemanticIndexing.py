from main import Executor
from logs.logger import *

if __name__ == "__main__":
    try :
        thisExecutor = Executor(NUMFILES=-1)
        thisExecutor.initiateCluster()

        thisCluster = thisExecutor.cluster
        

        if ( thisCluster == None ):
            raise Exception('Could not create cluster')

        thisCluster.instantiateDocuments()
        thisCluster.cleanCluster()
        reducedMatrix = thisCluster.latentSemanticModel().returnObject['reducedMatrix']

        print(reducedMatrix)
    except Exception as E:
        Log("", code='e', message=f"Could not create clean the Cluster : {str(E)}")
