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
        '''
        Gets the connection data from `extension_connections` collection in mongodb and preprocesses it for BM25 ranking.
        '''
        self.data = self.mongodb_client.get_all_connections()
        processed_data = []

        for doc in self.data:
            doc_text = doc['text'].lower()
            doc_body = doc['target_body'].lower() if('target_body' in doc)  else None
            doc_title = doc['target_title'].lower() if('target_title' in doc)  else None

            total_text = doc_text
            if(doc_title is not None):
                total_text += doc_title
            if(doc_body is not None):
                total_text += doc_body
            processed_data.append(total_text)


        #tokenizing
        nlp = spacy.load("en_core_web_sm")

        #Tokenising using SpaCy:
        for doc in tqdm(nlp.pipe(processed_data, disable=["tagger", "parser","ner"])):
            tok = [t.text for t in doc if t.is_alpha]
            self.tok_text.append(tok)
        
        self.bm25 = BM25Okapi(self.tok_text)

    def search(self, query):
        '''
        Ranks documents and returns the top ranked documents for a given query.
        '''
        if(self.bm25 is None):
            self.get_data_from_mongodb_and_tokenize()

        tokenized_query = query.lower().split(" ")
        results = self.bm25.get_top_n(tokenized_query, self.data, n=2)

        # results will contain jsons similar to
        #{  "_id": {    "$oid": "626586c2fdad4aeb0dc8ace0"  },  "time": 1650820802.436406,  "src_url": "https://answers.uillinois.edu/illinois.engineering/page.php?id=115238",  "tgt_url": "https://illinois.edu/",  "text": "UIUC homepage"}
        return results 