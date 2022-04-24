import pandas as pd
import spacy
from tqdm import tqdm
from rank_bm25 import BM25Okapi
import time
from pymongo import MongoClient

class BM25:
    def __init__(self, mongodb_client):
        self.data = []
        self.tok_text = []
        self.mongodb_client = mongodb_client
        self.bm25 = None
    
    def get_data_from_mongodb_and_tokenize(self):
        self.data = self.mongodb_client.get_all_connections()
        print(self.data)
        processed_data = [doc['text'].lower() for doc in self.data]

        #tokenizing
        nlp = spacy.load("en_core_web_sm")

        #Tokenising using SpaCy:
        for doc in tqdm(nlp.pipe(processed_data, disable=["tagger", "parser","ner"])):
            tok = [t.text for t in doc if t.is_alpha]
            self.tok_text.append(tok)
        
        self.bm25 = BM25Okapi(self.tok_text)

    def search(self, query):
        if(self.bm25 is None):
            self.get_data_from_mongodb_and_tokenize()

        tokenized_query = query.lower().split(" ")
        results = self.bm25.get_top_n(tokenized_query, self.data, n=2)

        # results will contain jsons similar to
        #{  "_id": {    "$oid": "626586c2fdad4aeb0dc8ace0"  },  "time": 1650820802.436406,  "src_url": "https://answers.uillinois.edu/illinois.engineering/page.php?id=115238",  "tgt_url": "https://illinois.edu/",  "text": "UIUC homepage"}
        return results 