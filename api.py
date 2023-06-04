
from neo4j import GraphDatabase
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
import numpy as np
from dotenv import load_dotenv
from flask import Flask,request,jsonify
from difflib import SequenceMatcher
import os
from flask_cors import CORS
import string
load_dotenv()

host = os.environ['HOST']
username = os.environ["USERNAME"]
password = os.environ["PASSWORD"]

conn = GraphDatabase.driver(host,auth=(username,password))


app = Flask(__name__)
CORS(app)

@app.route('/recommend/',methods=['GET', 'POST'])
def run_recommendation():
    inputText = request.form.get('inputText').title()
    # inputText = string.capwords(inputText)

    # inputText = 'drift'
    # if not inputText:
    #     return jsonify({'error': 'Missing inputText parameter'})
    
    with conn.session() as session:
        res = "MATCH (a:Anime) RETURN a.title AS title, a.genre AS genre, a.rating as rating,a.studio AS studio, a.show_type AS show_type"
        # for i in res:
        #     print(i)
        query = session.run(res)

        data = [(row['title'],row['genre'],row['rating'],row['studio'],row['show_type'])for row in query]

        empList = list()
        for title,genre,rating,studio,show_type in data:
            genre_split = [i for i in genre]
            empList.append((title,", ".join(genre_split),rating,studio,show_type))

        genres = [genre for _, genre, _, _ ,_ in empList]

        count_vec = CountVectorizer(binary=True)
        matrix = count_vec.fit_transform(genres).todense()
        np_array = np.asarray(matrix)

        similarity_matrix = cosine_similarity(np_array)
        title_index = None
        similarity_scores = None

        for i in range(len(empList)):
            title = empList[i][0]
            sim = SequenceMatcher()
            sim.set_seqs(inputText,title)
            if sim.ratio() > 0.4:
                title_index = i
                break
     
        if title_index is not None:
            similarity_scores = similarity_matrix[title_index]
            top_indices = np.argsort(similarity_scores)[::-1]
            
            recommendation = [[list(empList[i]),similarity_scores[i]*100] for i in top_indices if similarity_scores[i]>0.5]  
            res = {
                "status" : 200,
                "body" : recommendation
            }
        else:
            res = {
                "status" : 400,
                "body" : "Not Found"
            }
        return res

if __name__ == '__main__':
    app.run()
