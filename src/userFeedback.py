import sys
import re
import pprint
from googleapiclient.discovery import build
import RocchioSession

class userFeedback():
    """
    Class for handling the user relevance judgement.
    :Members:
        :query: string, a query that gets updated in each iteration,
        :clientKey: string, JSON API key for the user for calling the Google Search API,
        :engineKey: string, engine ID
        :precision: the specified precision level that is desired by the user.
    """
    def __init__(self, clientKey, engineKey, query, precision=0.9):
        self.query = query
        self.clientKey = clientKey
        self.engineKey = engineKey
        self.precision = precision
    
    def userFeedbackLoop(self):
        """
        Controls the entire user feedback loop. 
        """
        currentPrecision = 0.0
        relevantDocuments = list()
        googleResultSet = dict()
        while True:
            print("Parameters:")
            print("Client Key\t=\t", self.clientKey)
            print("Engine Key\t=\t", self.engineKey)
            print("Query     \t=\t", self.query)
            print("Precision \t=\t", str(self.precision))
            print("Google Search Results: ")
            print("=======================")
            relevantDocuments, googleResultSet, validDocumentCount = self.executeGoogleQuery()
            currentPrecision = len(relevantDocuments)/float(validDocumentCount)
            if self.checkPrecision(currentPrecision) == True:
                break
            print("=======================")
            print("FEEDBACK SUMMARY:")
            print("Precision: ", currentPrecision)
            print("Still below the desired precision of ", self.precision)
            print("Indexing Results...")
            updatedTokenizedQuery = self.expandQueryKeywords(relevantDocuments, googleResultSet)
            self.query = ' '.join(updatedTokenizedQuery)
    
    def executeGoogleQuery(self):
        """
        Executes the google api with a particular query, and returns the results.

        :params:
            :None
        :returns:
            :tuple, with
                :relevantDocumentSet: list, of relevant document indices,
                :resultSet: dictionary, of all the results returned by Google,
                :validDocumentCount: int, the number of html documents retrieved
        """
        googleService = build("customsearch", "v1", developerKey=self.clientKey)
        resultSet = googleService.cse().list(q=self.query, cx=self.engineKey).execute()
        documentSet = resultSet['items']
        validDocumentCount = 0
        relevantDocumentSet = list()
        for index in range(10):
            if 'fileFormat' in documentSet[index]:
                print("The result document was not in html format. Thus, it was ignored.")
                continue
            validDocumentCount += 1
            print("Result " + str(index + 1))
            print("[")
            print(" URL: ", documentSet[index]['link'])            
            try:
                print(" Title: ", documentSet[index]['title'])
            except:
                print(" Title: N/A")
            try:
                print(" Summary: ", documentSet[index]['snippet'])
            except:
                print(" Summary: N/A")
            print("]")
            print("Relevant(y/n): ")
            if re.search(r"^[Yy].*", input()) != None:
                relevantDocumentSet.append(index)     
        return relevantDocumentSet, resultSet, validDocumentCount

    def checkPrecision(self, currentPrecision):
        """
        Compares the current precision with the desired precision levels.

        :params:
            :currentPrecision: float, precision obtained on asking for user relevance
        :returns:
            :boolean, whether the precision requirements are satisfied or not.
        """
        if currentPrecision >= self.precision:
            print("=======================")
            print("FEEDBACK SUMMARY:")
            print("Precision: ", currentPrecision)
            print("The desired precision levels have been attained!")
            return True
        elif currentPrecision == 0.0:
            print("=======================")
            print("FEEDBACK SUMMARY:")
            print("Precision: ", currentPrecision)
            print("No relevant documents were found in the search results. Please enter another query.")
            return True
        return False
    
    # def checkYesOrNo(self, input):
    #     return re.search(r"^[Yy].*", input) != None

    def expandQueryKeywords(self, relevantDocumentSet, googleResultSet):
        """
        Calls the Rocchio algorithm and data preprocessing algorithms

        :params:
            :relevantDocumentSet: list, of relevant document indices,
            :googleResultSet: dictionary, of all the results returned by Google
        :returns:
            :list, tokenized expanded query based on user feedback
        """
        session = RocchioSession.QuerySession(self.query)
        return session.PreprocessQueryResults(googleResultSet, relevantDocumentSet)
    
def main():
    try:
        clientKey = sys.argv[1]
        engineKey = sys.argv[2]
        precision = float(sys.argv[3])
        query = sys.argv[4]
    except Exception as err:
        print("The script should be executed with the following format: ")
        print("python3 script.py <clientKey> <engineKey> <precision> '<query>'")
        return
    userObject = userFeedback(clientKey, engineKey, query, precision)
    userObject.userFeedbackLoop()

if __name__=='__main__':
    main()
