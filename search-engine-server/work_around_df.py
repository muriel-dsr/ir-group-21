import pandas as pd
import random
from db.services_pymongo import documents
from tqdm import tqdm
from retrieval_custom_preprocess import custom_preprocess

import csv


def doc_custom_workaround():
    """
    returns a dataframe of 5k documents and their clinical_id
    """
    n_docs = 5000
    corpus = random.sample(list(documents.find({}, {"clinical_id": 1, "raw_text": 1})), n_docs)

    docs = pd.DataFrame(corpus)
    docs = docs[['clinical_id', 'raw_text']]
    docs.rename(columns={'clinical_id': 'docno', 'raw_text': 'text'}, inplace=True)

    docs_custom = docs.copy()
    docs_custom['text2'] = ''

    for i in tqdm(range(len(docs_custom))):
        text = docs_custom.iloc[i].text
        removed = custom_preprocess(text)
        docs_custom.loc[i, 'text2'] = removed

    docs_custom = docs_custom.drop(['text'], axis=1)
    docs_custom = docs_custom.rename(columns={"text2": "text"})

    docs_custom.to_csv('docs_custom.csv')

    return docs_custom

docs_custom = doc_custom_workaround()



# file = open("docs_custom.csv", "r")
# data = list(csv.reader(file, delimiter=","))

# docs_custom = pd.read_csv('docs_custom.csv')
# print(docs_custom)

