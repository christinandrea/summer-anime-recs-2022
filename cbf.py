from neo4j import GraphDatabase
from sklearn.metrics.pairwise import pairwise_distances,cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
import numpy as np

# from sklearn.metrics import pairwise_distances

host = 'bolt://localhost:7687'
username = 'neo4j'
password = 'Jaehyun14*'

conn = GraphDatabase.driver(host,auth=(username,password))

inputText = input("Enter title: ")


with conn.session() as session:
    res = "MATCH (a:Anime) RETURN a.title AS title, a.genre AS genre, a.rating as rating,a.studio AS studio, a.show_type AS show_type"

    query = session.run(res)

    data = [(row['title'],row['genre'],row['rating'],row['studio'],row['show_type'])for row in query]

    empList = list()
    for title,genre,rating,studio,show_type in data:
        genre_split = [i for i in genre]
        empList.append((title,", ".join(genre_split),rating,studio,show_type))

    genres = [genre for _, genre, _, _ ,_ in empList]

    count_vec = CountVectorizer(binary=True)
    genre_matrix = count_vec.fit_transform(genres).todense()
    np_array = np.asarray(genre_matrix)
    # similarity_matrix = pairwise_distances(np_array, metric='jaccard')
    similarity_matrix = 1 - cosine_similarity(np_array)
    title_index = None
    for i, (title, _, _,_,_) in enumerate(empList):
        if title == inputText :
            title_index = i
            break
    if title_index is None:
        print("Show not found")

    # print(genre_matrix)
    similarity_scores = similarity_matrix[title_index]
    print(similarity_matrix[title_index])
    
    # print(similarity_matrix[title_index])
    top_indices = similarity_scores.argsort()[::1][:5]
    recList = []
    
    # for i in top_indices:
    #     recommendations = (empList[i[0]],similarity_scores[i[0]])
    #     # total_recs = recommendations
    #     recList.append(recommendations)
    #     if len(recList)>=3:
    #         break


    recommendation = [(empList[i], similarity_scores[i]) for i in top_indices]
    recList.append(recommendation)

    # recommendations = [(empList[i],similarity_scores[i]) for i in top_indices]




# print(recList)

for i in recList:
    del i[0]
    for items in i:
        print(items)

        
    