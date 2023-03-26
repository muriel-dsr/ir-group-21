import os
from db import process_clinical_trial


def process_corpus(dir: str):
    """
    Adds new documents to the database and adds them to the corpus term-document matrix.

    Takes the path of the directory containing all the documents as an input and searches through the directory to find
    the xml files. Then takes each file and adds it to the database and concatenates the document term-frequency matrix
    with the term-document matrix.

    :param dir: str
    :return: None
    """
    if not os.path.exists(dir):
        return
    # get all documents in the dataset
    docs = list()
    for dirpath, dirnames, filenames in os.walk(dir):
        for name in filenames:
            path = os.path.join(dirpath, name)
            if path.split('.')[-1] == 'xml':
                docs.append(path)
    # process documents
    for index, doc in enumerate(docs):
        print(f'processing {index} / {len(docs)} || {round(100 / len(docs) * index)}% || doc name: {doc}')
        process_clinical_trial(doc)


# Run this file as standalone to process the dataset.
if __name__ == '__main__':
    # Add full path to the directory (folder) containing the documents.
    path = ""
    process_corpus(path)
