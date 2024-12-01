from pymongo import MongoClient
from sklearn.feature_extraction.text import TfidfVectorizer
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

# create database connection object using pymongo
DB_NAME = "hw4"
DB_HOST = "localhost"
DB_PORT = 27017

try:
    client = MongoClient(host=DB_HOST, port=DB_PORT)
    db = client[DB_NAME]
    terms = db['terms']
    docs = db['documents']
except:
    print("Database not connected successfully")

# testing purposes -- delete later
docs.delete_many({})
terms.delete_many({})

document_list = ["After the medication, headache and nausea were reported by the patient.",
            "The patient reported nausea and dizziness caused by the medication.",
            "Headache and dizziness are common effects of this medication.",
            "The medication caused a headache and nausea, but no dizziness was reported."]

# instantiate the vectorizer object
tfidfvectorizer = TfidfVectorizer(analyzer='word', ngram_range=(1,3))

# convert document set into a matrix using .fit_transform()
tfidfvectorizer.fit(document_list)
doc_v = tfidfvectorizer.transform(document_list)

vocabulary = tfidfvectorizer.vocabulary_

# retrieve terms found in the corpora
tfidf_tokens = tfidfvectorizer.get_feature_names_out()

# display term matrix using data frame
print("TD-IDF Vectorizer \n")
tfidf_matrix = pd.DataFrame(data = doc_v.toarray(), index = ['Doc1', 'Doc2', 'Doc3', 'Doc4'], columns = tfidf_tokens)

# add documents into mongodb collection
for term, position in vocabulary.items():
    docs_with_term = [
        {
            "doc_id": doc_id,
            "tf_idf": tfidf_matrix.at[doc_id, term]
        }
        for doc_id in tfidf_matrix.index if tfidf_matrix.at[doc_id, term] > 0
    ]
    terms.insert_one({
        "_id": position,
        "position": position,
        "docs": docs_with_term
    })

# add documents to mongodb documents collection
doc_id = 1
for document in document_list:
    docs.insert_one({'_id': doc_id, 'content': document})
    doc_id += 1

# rank the documents using the vector space model according to the queries
queries = [
    "nausea and dizziness",
    "effects",
    "nausea was reported",
    "dizziness",
    "the medication"
]

# vectorize the queries
query_matrix = tfidfvectorizer.fit_transform(document_list)
query_vector = tfidfvectorizer.transform(queries)

# compute pairwise cosine similarity
cosine_sim = cosine_similarity(query_vector, tfidf_matrix)

# output doc content and score
for query_index, query in enumerate(queries):
    print(f"Query {query_index + 1}: '{query}'")

    # filter out zero similarities and sort score in descending order
    scores = [
        (doc_index, similarity)
        for doc_index, similarity in enumerate(cosine_sim[query_index])
        if similarity > 0
    ]
    scores = sorted(scores, key=lambda x: x[1], reverse = True)

    for doc_index, similarity in scores:
        print(f"    '{document_list[doc_index]}', {similarity:.3f}")
    print()