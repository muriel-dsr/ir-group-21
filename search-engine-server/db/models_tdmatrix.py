from bson.objectid import ObjectId
import pandas as pd
from pandas.core.frame import DataFrame
import os
import pickle


class TermDocumentMatrix:
    """
    A term document matrix for all documents in the corpus.

    Attributes

    _id: ObjectId | None - database id for the document
    corpus_name: str | None - name of the corpus
    matrix: DataFrame | str | None - a pandas dataframe representation of document-term-frequencies

    Methods

    info: dict - return all class variables as a dictionary

    save_matrix: bool - saves the term document matrix for the corpus as a pickle file.

    add_new_document: bool - adds a new document (df) to the term-document matrix.

    """
    def __init__(self, doc: dict | None = None):
        self._id: ObjectId | str | None = None
        self.corpus_name: str | None = None
        self.matrix: DataFrame | str | None = None

        # If document exists assign each value pair to the respective value pair for class instance
        if doc:
            for k, v in doc.items():
                setattr(self, k, v)
            if 'matrix' in doc.keys() and type(doc['matrix']) == str:
                self.matrix = pd.read_json(doc['matrix'])

    def info(self):
        """
        Return all class variables as a dictionary.

        :return: dict
        """
        return {
            "_id": self._id,
            "corpus_name": self.corpus_name,
            "matrix": self.matrix
        }

    def save_matrix(self):
        """
        Saves the term document matrix for the corpus as a pickle file.

        :return: bool
        """
        try:
            path = os.path.join(os.getcwd(), f'{self.corpus_name}.pkl')
            with open(path, 'wb') as f:
                pickle.dump(self, f)
            return True
        except Exception as e:
            print('Error:', e)
            return False

    def add_new_document(self, df: DataFrame):
        """
        Adds a new document (df) to the term-document matrix.

        :param df: DataFrame
        :return: bool
        """
        try:
            self.matrix = pd.concat([self.matrix, df], join='outer')
            self.matrix = self.matrix.fillna(0.0)
            self.save_matrix()
            return True
        except Exception as e:
            print(f'Error: failed to add new document to matrix', e)
            return False
