import re
from pymongo import MongoClient

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

# add documents into mongodb collection
doc_id = 1
for document in document_list:
    docs.insert_one({'_id': doc_id, 'content': document})
    doc_id += 1

# initialize set that contains all words visited
vocab = {}

# tokenize documents
term_id = 1
for document in docs.find():
    doc_id = document['_id']
    content = document['content']

    # make lowercase and remove punctuation
    words = re.findall(r'\w+', content.lower())

    # make unigrams, bigrams and trigrams
    unigrams = words
    bigrams = [' '.join(words[i:i+2]) for i in range(len(words) - 1)]
    trigrams = [' '.join(words[i:i+3]) for i in range(len(words) - 2)]

    n_grams = unigrams + bigrams + trigrams

    print(n_grams)

    # combine all n-grams into single list to use as new words list
    for word in words:       
        if word not in vocab:
            # not visited, so insert new document and add doc_id for term
            vocab[word] = term_id
            terms.insert_one({
                '_id': term_id,
                'pos': term_id,
                'docs': [{'doc_id': doc_id}]
            })
            term_id+=1
        else:
            # visited, so update document with matching term_pos and add to doc_id list
            term_pos = vocab[word]
            terms.update_one(
                {'_id': term_pos},
                {'$addToSet': {'docs': {'doc_id': doc_id}}}
            )

