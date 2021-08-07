import nltk
nltk.download('stopwords')
nltk.download('punkt')
from nltk.stem import *
from nltk.tokenize import word_tokenize
from collections import defaultdict
import sys
import math
import json

class QuerySession():
    """
    # Class Params: 
        - InvertedList: Dictionary for each term that exists in the search-result collection. Contains calculated IDF, and weight
        - Query: Updated query terms
        - SearchResults: Tokenized results returned from Google Search API
        - Alpha, Beta, Gamma: Optional query hyperparams. Default set similar to textbook
    """
    def __init__(self, query, beta = .75, gamma = .75):
        self.InvertedList = dict() # Store IDF later on as well as documents that exist in.
        self.SearchResults = dict()
        self.Query = [query]
        self.Beta = beta
        self.Gamma = gamma
        self.Stemmer = PorterStemmer()

    """
    # Function: PreprocessQueryResults
    # Params: Query results from Search API
    # Do: Preprocess raw query data and store as tokenized documents
    """
    def PreprocessQueryResults(self, QueryResults, RelevantDocuments):
        # print(self.Query)
        stopwords = set(nltk.corpus.stopwords.words('english')) #Fetch nltk stopwords

        toTokenize = ['title', 'snippet']
        for documentIndex in range(len(QueryResults['items'])): # Loop through each document
            tokenized_document = list()
            #Tokenize pre-specified sections
            for section in toTokenize:
                try:
                    text = QueryResults['items'][documentIndex][section]
                    # print("About to preprocess section: ", section)
                    text = word_tokenize(text) # Use ntlk to tokenize
                    text = [word.lower() for word in text if ((len(word) > 1) and word.lower() not in stopwords and word.isalpha())]
                    tokenized_document += text
                except:
                    pass
            # print("For document ", documentIndex, " tokenized form is: ", tokenized_document)
            self.SearchResults[documentIndex] = tokenized_document
        
        # Lastly, update index after all documents have been tokenized
        return self.UpdateIndex(RelevantDocuments)

    """
    # Function: UpdateIndex
    # Params: None
    # Do: Generate updated InvertedList to be used by Rocchio Algorithm
    # InvertedList Structure:
        {
            "term1": 
            {
                "IDF": log(len(SearchResults[items])/(len(self.InvertedList[RelevantDocs]) + len(self.InvertedList[NonRelevantDocs])))
                "Weight": = self.Beta/len(RelevantDocs) * tf-idf - self.Gamma/len(RelevantDocs) * tf-idf #Need to loop over each doc to calculate
                "RelevantDocs": {
                    "doc1": 4, # Can replace doc name with doc index within SearchResults.items
                    "doc3": 5,
                },
                "NonRelevantDocs": {
                    "doc2": 2,
                    "doc4": 1,
                }
            },
            "term2":...
        }
    """
    def UpdateIndex(self, relevantDocs):
        # relevantDocs = set([0,1,2,3,4])
        for documentIndex in self.SearchResults.keys():
            for word in self.SearchResults[documentIndex]:
                if word not in self.InvertedList: # Create new word entry if does not exist
                    self.InvertedList[word] = self.CreateNewIndex()
                if documentIndex in relevantDocs:# Create new word entry if does not exist 
                    self.InvertedList[word]['RelevantDocs'][documentIndex] += 1
                else:
                    self.InvertedList[word]['NonRelevantDocs'][documentIndex] += 1

        for word in self.InvertedList.keys(): # Calculate IDF for each word entry in collection"
            self.InvertedList[word]['IDF'] = math.log10(len(word))+ math.log10(len(self.SearchResults.keys())/(len(self.InvertedList[word]['RelevantDocs'].keys()) + len(self.InvertedList[word]['NonRelevantDocs'].keys())))
        # print(json.dumps(self.InvertedList))
        self.relevantDocs = relevantDocs
        return self.GetNewQuery()
        # return 

    """
    # Function: CreateNewIndex
    # Params: None
    # Do: Generates and returns empty template for new InvertedIndex entry
    """
    def CreateNewIndex(self):
        newEntry = defaultdict()
        newEntry['IDF'] = None
        newEntry['Weight'] = 0
        newEntry['RelevantDocs'] = defaultdict(lambda:0)
        newEntry['NonRelevantDocs'] = defaultdict(lambda:0)
        return newEntry
    
    """
    # Function: GetNewQuery
    # Params: None
    # Do: Apply Rocchio Algorithm to update weights and return an updated Query based on top ranked weight
    # Source: Methodology for tf-idf based Rocchio: http://www.cs.cmu.edu/~wcohen/10-605/rocchio.pdf, 
    """
    def GetNewQuery(self):
        for word in self.InvertedList.keys(): # For each word, calculate weight based on Rocchio for Relevant and Non-relevant documents
            idf = self.InvertedList[word]['IDF']
            for documentIndex in self.InvertedList[word]['RelevantDocs'].keys():
                tf = 1 + math.log10(self.InvertedList[word]['RelevantDocs'][documentIndex])
                self.InvertedList[word]['Weight'] += self.Beta/len(self.InvertedList[word]['RelevantDocs'].keys()) * tf * idf
            for documentIndex in self.InvertedList[word]['NonRelevantDocs'].keys():
                tf = 1 + math.log10(self.InvertedList[word]['NonRelevantDocs'][documentIndex])
                self.InvertedList[word]['Weight'] -= self.Gamma/len(self.InvertedList[word]['NonRelevantDocs'].keys()) * tf * idf
        appendedTerms = []
        appendedCount = 0
        sortedList = sorted(self.InvertedList, key=lambda word: self.InvertedList[word]['Weight'], reverse=True)

        prevQueries = set()
        for word in self.Query:
            prevQueries.add(word.lower())
            prevQueries.add(self.Stemmer.stem(word))
        for word in sortedList:
            if word.lower() not in prevQueries and len(self.InvertedList[word]['RelevantDocs'].items())>min(2, len(self.relevantDocs)):
                self.Query.append(word)
                appendedCount += 1
            if appendedCount == 2:
                break
        # If unable to find 2 words to append, then add first word in sortedlist just to move search along
        if appendedCount < 2:
            for word in sortedList:
                if word not in prevQueries:
                    self.Query.append(word)
                    appendedCount += 1
                if appendedCount == 2:
                    break
        return self.Query
