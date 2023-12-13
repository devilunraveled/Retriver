## Assignment 1 IRE

### Task 1

```python
    executor = Executor()
    executor.startExecutionIndividual()
```
This essentially creates the Executor object, and instructs it to parse the documents independently, creating frequency charts and tag-clouds for each document, to modify this behaviour, simply change the following code.

```python
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
```

The `displayWordCloud()` and `plotFrequencies()` methods perform exactly what you'd think they perform.


> Note If you want to perform the operations, without stemming or stop-word removal, you can pass it as arguments to the `cleanDocument()` method as follows :

> `cleanDocument(performStemming=False, performStopWordRemoval=False)`. Note that the default values of both these arguments is `True`.

### Task 2 

```cpp
    executor = Executor()
    executor.startExecutionCluster()
```

Similar changes in the Cluster class can also make the code customizable.
