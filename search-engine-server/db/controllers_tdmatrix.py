from db.models_tdmatrix import TermDocumentMatrix
from pandas.core.frame import DataFrame
import os
import pickle


def load_matrix(corpus_name: str):
    """
    Determines if an instance of TermDocumentMatrix exists for the corpus and returns it. Else, creates a new one.

    :param corpus_name: str
    :return: TermDocumentMatrix
    """
    try:
        pickle_file = os.path.join(os.getcwd(), f'{corpus_name}.pkl')
        with open(pickle_file, 'rb') as pf:
            matrix: TermDocumentMatrix = pickle.load(pf)
        return matrix
    except FileNotFoundError:
        matrix: TermDocumentMatrix = TermDocumentMatrix({'corpus_name': corpus_name})
        matrix.save_matrix()
        return matrix


def get_clinical_td_matrix():
    """
    Returns the TermDocumentMatrix specific to the clinicaltrials.gov corpus
    :return: TermDocumentMatrix
    """
    return load_matrix('clinicaltrials.gov')


def update_clinical_td_matrix(doc: DataFrame):
    """
    Adds a new term-document matrix to the Corpus DataFrame
    :param doc: DataFrame
    :return: bool
    """
    try:
        matrix = get_clinical_td_matrix()
        if type(doc) == DataFrame:
            matrix.add_new_document(doc)
        return True
    except Exception as e:
        print('Error: failed to update term document matrix with new document:', e)
        return False
