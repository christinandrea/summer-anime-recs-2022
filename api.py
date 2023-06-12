
from neo4j import GraphDatabase
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
import numpy as np
from dotenv import load_dotenv
from flask import Flask,request
from difflib import SequenceMatcher
import os
from flask_cors import CORS

load_dotenv()
# Load credentials from .env 
host = os.environ['HOST']
username = os.environ["USERNAME"]
password = os.environ["PASSWORD"]

#Connect credentials to database
conn = GraphDatabase.driver(host,auth=(username,password))

#Initiate flask and CORS
app = Flask(__name__)
CORS(app)
#Create API Endpoint
@app.route('/recommend/',methods=['GET', 'POST'])
def run_recommendation():
    #Get input text from AJAX
    inputText = request.form.get('inputText').title()
 
    with conn.session() as session:
        #Initiate neo4j query
        res = "MATCH (a:Anime) RETURN a.title AS title, a.genre AS genre, a.rating as rating,a.studio AS studio, a.show_type AS show_type"
      
        query = session.run(res)
        #Create a list and put data from query into the list as tuple
        data = [(row['title'],row['genre'],row['rating'],row['studio'],row['show_type'])for row in query]
        #Initiate empty list
        empList = list()
        #Iterate each data in data list 
        for title,genre,rating,studio,show_type in data:
            #Split the genre 
            genre_split = [i for i in genre]
            #Append all the data and the split genre into empList
            empList.append((title,", ".join(genre_split),rating,studio,show_type))

        # iniate a list only for genre in empList ; ignore any other variable ; this will be used for counting similarity score 
        genres = [genre for _, genre, _ , _ ,_ in empList]
        #Initiate the CountVectorizer
        count_vec = CountVectorizer(binary=True)
        #Create a matrix of genre ; this will make a scalar type matrix
        matrix = count_vec.fit_transform(genres).todense()
        #Change the matrix datatype to array
        np_array = np.asarray(matrix)
        #Count the cosine similarity for genre using np_array
        similarity_matrix = cosine_similarity(np_array)
        #Initiate index for title and similarity score as None
        title_index = None
        similarity_scores = None
        #Iterate according empList length
        for i in range(len(empList)):
            #Get the title only from empList
            title = empList[i][0]
            #Initiate SequenceMatcher() 
            sim = SequenceMatcher()
            # Use set_seqs function from SequenceMatcher to count ratio between the input title from user and the title in database
            sim.set_seqs(inputText,title)
            # If the ratio is more than 40%, it will set the title index according to the index of the title placed
            if sim.ratio() > 0.4:
                title_index = i
                break
        
        if title_index is not None:
            # If the title index is not None, set the similarity scores using similarity matrix and the title_index 
            similarity_scores = similarity_matrix[title_index]
            #Flip the array of similarity scores in order the most similar will be on top
            top_indices = np.argsort(similarity_scores)[::-1]
            # Create a list for the recommendation data and its similarity score if the similarity score is more than 75% 
            recommendation = [[list(empList[i]),similarity_scores[i]*100,title_index,sim.ratio()] for i in top_indices if similarity_scores[i]>0.75]  
            # Initiate res variable to create a JSON format as response to front-end side
            # 200 is if there's any recommendation found
            res = {
                "status" : 200,
                "body" : recommendation
            }
        else:
            # 400 is if there isn't any recommendation 
            res = {
                "status" : 400,
                "body" : "Not Found"
            }
        return res
# Run the API
if __name__ == '__main__':
    app.run()

## NOTE  ## 
# The ratio of input title from user and the title from database has to be counted first before determining the title index for similarity count. #
# ratio of title ≠ similarity score for recommendation #
# the first data to display doesnt always the title we meant to search because it depends on the ratio count. #