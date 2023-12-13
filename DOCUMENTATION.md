### Code Structure Documentation

#### Classes

- As you might already have seen, the `/classes` folder hosts many of the classes that are used to simplify the workflow.
- Let's go over them one by one to better understand their use-case.

1. **Info.py**
    - This is pretty easy to understand class, it implements what I term the `Response` objects, every function returns some
    kind of a return object, where it can pass relevant information regarding the execution. 

2. **Visual.py**
    - This class holds the code for the two different visualizations associated with this assignment.
    - The first one is that of WordCloud which I have termed `TagCloud` in context of the assignment.
    - The second one implements the frequency plot based on the `vocabulary` of passed to it.

3. **Document.py**
    - This is the first major class as it stores the entirity of relevant information regarding the document under consideration.
    - It has many methods, each named unambigously, for ease of understanding.

4. **Cluster.py**
    - This class stores clusters of documents to create visualizations over a group of documents rather than over each document individually.
    - Has methods names after the methods in the `Document` class itself.


### Other classes/functions
1. **logger**
    - This is probably the most simple class, as its sole purpose is to provide wrapper functions over the print statement
    for debugging/logging and error handling pueposes.

2. **Task**
    - This is another straight forward class, dedicated to running the tasks given a document to run them over, it has a sisterClass called
    `ClusterTasks` present in the same file.

3. **Executor**
    - This class instantiates an Executor object that executes all the tasks for different documents in isolation.

4. **Cleaning**
    - This code performs the preprocessing of the documents, removing punctuations using REGEX expression.
    - Also removes the stop words, performs stemming and creates the vocabulary of the document.
