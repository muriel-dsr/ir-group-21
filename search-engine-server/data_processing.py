import os
from db import process_clinical_trial, Document, get_clinical_td_matrix, get_documents_for_matrix
import pandas as pd
from datetime import datetime as dt
import datetime


def process_corpus(directory: str):
    """
    Adds new documents to the database and adds them to the corpus term-document matrix.

    Takes the path of the directory containing all the documents as an input and searches through the directory to find
    the xml files. Then takes each file and adds it to the database and concatenates the document term-frequency matrix
    with the term-document matrix.

    :param directory: str
    :return: None
    """
    if not os.path.exists(directory):
        return
    # get all documents in the dataset
    docs = list()
    for dir_path, _, filenames in os.walk(directory):
        for name in filenames:
            path = os.path.join(dir_path, name)
            if path.split('.')[-1] == 'xml':
                docs.append(path)
    # process documents
    for index, doc in enumerate(docs):
        print(f'processing {index} / {len(docs)} || {round(100 / len(docs) * index)}% || doc name: {doc}')
        process_clinical_trial(doc)
    print('corpus processing completed')


def calculate_dt_matrix():
    """
    Adds documents to the term-document matrix.

    :return: None
    """
    print('calculating document term matrix ...')
    total_time = datetime.timedelta(0)
    start_time = dt.now()
    tdm = get_clinical_td_matrix()
    matrix = pd.DataFrame()
    docs = [Document(doc) for doc in get_documents_for_matrix(tdm.matrix.index)]
    for index, doc in enumerate(docs):
        matrix = pd.concat([matrix, doc.term_matrix], join='outer')
        if index % 20 == 0 or index == len(docs) - 1:
            matrix = matrix.fillna(0.0)
            tdm.matrix = pd.concat([tdm.matrix, matrix])
            matrix = pd.DataFrame()

    time_diff = dt.now() - start_time
    total_time += time_diff
    tdm.save_matrix()

    print(f'New matrix shape: {tdm.matrix.shape} created in {total_time}')
    return


# Run this file as standalone to process the dataset.
if __name__ == '__main__':
    # Add full path of the directory (folder) containing the documents to the variable path.
    directory_path = ""
    process_corpus(directory_path)
    for i in range(500):
        calculate_dt_matrix()
