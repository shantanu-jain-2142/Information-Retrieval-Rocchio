# Information-retreival-ADB
Designing an Information Retrieval Model with Precision @10. Implementing an IR model based on user relevance feedback (yes/no mechanism), to expand the query for better satisfaction of the user's information needs.

# Team Members

Phan Anh Nguyen (pn2363)

Shantanu Lalitkumar Jain (slj2142)

# Project Structure
- /src
    - userFeedback.py
    - RocchioSession.py
- /transcripts
    - transcript_1_per_se.txt
    - transcript_2_brin.txt
    - transcript_3_cases.txt
- requirements.txt
- README.md

# List of Files

- RocchioSession.py
- userFeedback.py
- transcript_1_per_se.txt
- transcript_2_brin.txt
- transcript_3_cases.txt
- requirements.txt
- README.md

# Environment
- Python Version: 3.6.9
- NLTK: 3.5

# Instructions
Please follow the below mentioned instructions for running our program in the VM:
1. Go to the project folder
```
cd proj1/
```
2. Install the dependencies,
```
pip3 install -r requirements.txt
```
3. Run the driver program with the required arguments (mentioned below)
**NOTE**: Remember to add the query in quotes for multi word query. Otherwise the system would consider only the first word as query.
```
python3 src/userFeedback.py <clientKey> <engineKey> <precision> "<query>"
```

# Project design

Our product code is split into two files: A main driver ("userFeedback.py") and a defined QuerySession class for implementing the query modification ("RocchioSession.py") for each search iteration. The flow of our program works as follows: 

1. The user starts the program with a search term from the command line and desired precision level
2. Our driver will then call the Google Custom Search API on the provided query terms and display the top 10 results. Here we use the [Google API Client Discovery](https://developers.google.com/discovery) service to call the API and collect the result documents.
3. User gets to add the relevance for each of the presented documents based on a simple "Yes/No" feedback mechanism.
4. User feedback is consolidated.
5. A new QuerySession is instantiated and ingests the JSON file returned from the Google Custom Search API as well as the consolidated user feedback. 
6. Within QuerySession, we use the *nltk* libraries to construct a vectorized representation of each document returned in the JSON and use that to construct the inverted list and carry out query modification (described in more detail below). We ultimately return an updated query vector to the driver for the next search iteration. 
7. Once the search precision has reached the specified threshold or is equalt to 0.0, our driver will exit.

# Query-Modification methodology

Our Query-Modification technique utilizes the Rocchio algorithm explained in lecture. For each search iteration, we instantiate a QuerySession, which takes in the query results returned from the Search Engine API and creates an inverted list of all terms that exist within the 'Title' and 'Snippet' fields. Fields within the inverted list are: [IDF], [Weight], [RelevantDocs], [NonRelevantDocs]. 

We then assign individual document term weights to each of the terms that exist by calculating *tf-idf*. We then used Rocchio to generate a new set of weights for each term based on predetermined Beta and Gamma values. We eventually settled for **Beta = 0.75** and **Gamma=0.75**. Alpha values were **not** used as we were not allowed to modify or remove original query terms once inserted as per the assignment specifications. 

Finally, we sorted terms by weight and applied and applied several additional filters to determine the top 2 words to be appended to the query (if not already present). Specifically, we used stemming to filter out potential repeat words (i.e: "Cases" and "Case") from being inserted into query updates, as well as preferred to add terms that existed in at least 2 relevant documents where possible. We noticed that the latter filter greatly increased our precision in the earlier iterations. 

# Handling of Non-HTML files

For the purpose of our project, we have decided to ignore the non-html files. Therefore, any document set retrieved from the search engine, which is not a html file, will be ignored and **not** considered for precision and query expansion calculations. 


# References
- [Rocchio Algorithm from Wikipedia](https://en.wikipedia.org/wiki/Rocchio_algorithm)
- [Google API Client Discovery](https://developers.google.com/discovery)
- [Natural Language ToolKit Library](https://www.nltk.org/)
- Methodology of tf-idf weights using Rocchio: http://www.cs.cmu.edu/~wcohen/10-605/rocchio.pdf
