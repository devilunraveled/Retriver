import os

# Paths
SOURCE = os.path.abspath("corpus/") + "/"
DESTINATION = os.path.abspath("data/") + "/"

# Global variables 
SEPARATOR = '\n'

#STOP WORDS
STOPWORDS = set((""))
STOPFILE = os.path.abspath("english.stop")

OUTPUT_LIMIT = 15

with open(STOPFILE, 'r') as words :
    for word in words.readlines():
        STOPWORDS.add(word.rstrip('\n'))
