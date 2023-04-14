from datetime import datetime as dt
from db import process_clinical_trial, Document, get_clinical_td_matrix, get_documents_for_matrix, process_query
from db import create_all_indexes
import datetime
import os
import pandas as pd
import pathlib

''' Processes the documents and loads the dataset to MongoDB '''

def judgement():
    """
    Load the .txt file that contain the relevance judgement, then split the data into columns.
    Choose the index of the column that contains the document ids.
    set() lists the unique values.

    :return: all the document id with relevance judgement
    """
    with open('qrels2021.txt', 'r') as file:

        unique_values = set()

        for line in file:
            columns = line.split()
            document_id = columns[2]  # index number of column with doc ids
            unique_values.add(document_id)

    return unique_values


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

    unique_values = judgement()
    xml_files = []
    filtered_files = []

    # Get all the documents stored in multiple sub-folders in the directory
    for subdir, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.xml'):
                file_path = os.path.join(subdir, file)
                xml_files.append(file_path)

    # Filter through the documents to get xml files with relevance judgements
    for file_path in xml_files:
        doc_id = file_path.split('/')[-1][:-4]
        if doc_id in unique_values:
            filtered_files.append(file_path)

    # process documents
    for index, doc in enumerate(filtered_files):
        print(f'processing {index} / {len(filtered_files)} || {round(100 / len(filtered_files) * index)}% || doc name: {doc}')
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


def extract_relevancy_data():
    """
    Finds the path for the Text Retrieval Conference clinical dataset relevancy and query lists and processes them.
    :return:
    """
    relevancy_path = os.path.join(pathlib.Path(__file__).parent.resolve(), 'qrels2021.txt')
    query_path = os.path.join(pathlib.Path(__file__).parent.resolve(), 'topics2021.xml')
    process_query(relevancy_path, query_path)


# Run this file as standalone to process the dataset.
if __name__ == '__main__':
    create_all_indexes()

    # # Add full path of the directory (folder) containing the documents to the variable path.
    directory_path = ""
    if not directory_path:
        print('You have not added a directory path... This caused a FileNotFoundError')
        raise FileNotFoundError

    process_corpus(directory_path)
    #
    # # Process relevancy
    extract_relevancy_data()
    #
    # # calculate document-term frequency matrix
    for i in range(500):
        calculate_dt_matrix()
