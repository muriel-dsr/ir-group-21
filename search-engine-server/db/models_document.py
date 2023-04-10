from db.services_pymongo import documents
from bson.objectid import ObjectId
import pandas as pd
from pandas.core.frame import DataFrame


class Document:
    """
    This class contains all properties and methods for a document in the corpus


    Attributes

    _id: ObjectId | None - database id for the document

    title: str | None - title of the document

    url: str - url for the document

    domain: str | None - the url domain for the document

    description: str | None - a brief description of the document for client / ui display

    raw_text: str | None - all text in the xml document without tags

    clinical_id: str | None - the clinical id given to the document by trec

    links_outgoing: int - number of links contained in the document (measure of authority)

    references: int - number of times the document has been referenced by other documents in the corpus

    term_frequencies: dict | None - dictionary of terms within the document and their frequency count

    term_matrix: DataFrame | None - a pandas dataframe representation of term frequencies

    clicks: int - total number of times the document has been viewed

    crawled: bool -  whether document has been fully processed or not

    crawl_success: bool - whether document has been successfully crawled without errors

    alive: bool - whether document url has a success response

    content_type: str - document url header type


    Methods

    info: dict - return all class variables as a dictionary

    info_db: dict - return all class variables for creating / updating the database

    info_client: dict - return all class variables relevant for client / ui

    create_document: bool - adds the document to the database

    update_document: bool - updates the relevant document in the database.

    create_term_matrix: bool - creates a term-matrix for the document and updates the database record with it.

    """
    def __init__(self, doc: dict = None):
        """
        Initialise all variables in class and generate variables that rely on others.
        """
        # Identifying information
        self._id: ObjectId | str | None = None
        self.title: str | None = None
        self.url: str = ""
        self.domain: str | None = None
        self.description: str | None = None
        self.raw_text: str | None = None
        self.tf_text: str | None = None
        self.clinical_id: str | None = None

        # Document indexing / relevance measures
        self.links_outgoing: int = 0
        self.references: int = 0
        self.term_frequencies: dict | None = None
        self.term_matrix: DataFrame | str | None = None
        self.clicks: int = 0

        # Processing status variables
        self.crawled: bool = False
        self.crawl_success: bool = False
        self.alive: bool = True
        self.content_type: str | None = None

        # If document exists assign each value pair to the respective value pair for class instance
        if doc:
            for k, v in doc.items():
                setattr(self, k, v)
            if self.term_matrix and type(self.term_matrix) == str:
                self.term_matrix = pd.read_json(doc['term_matrix'])

    def info(self):
        """
        Return all class variables as a dictionary.

        :return: dict
        """
        return {
            "_id": self._id,
            "title": self.title,
            "url": self.url,
            "domain": self.domain,
            "description": self.description,
            "raw_text": self.raw_text,
            "tf_text": self.tf_text,
            "clinical_id": self.clinical_id,

            "links_outgoing": self.links_outgoing,
            "references": self.references,
            "term_frequencies": self.term_frequencies,
            "term_matrix": self.term_matrix,
            "clicks": self.clicks,

            "crawled": self.crawled,
            "crawl_success": self.crawl_success,
            "alive": self.alive,
            "content_type": self.content_type,
        }

    def info_db(self):
        """
         Return all class variables (excluding self._id) as a dict for the purpose of creating / updating the database

        :return: dict
        """
        info = self.info()
        del info["_id"]
        if type(self.term_matrix) == DataFrame:
            info['term_matrix'] = self.term_matrix.to_json()
        return info

    def info_client(self):
        """
        Return all class variables relevant for client / ui

        :return: dict
        """
        return {
            "_id": str(self._id),
            "title": self.title,
            "url": self.url,
            "description": self.description
        }

    def create_document(self):
        """
        Adds the document to the database.

        :return: bool
        """
        try:
            inserted = documents.insert_one(self.info_db())
            self._id = ObjectId(inserted.inserted_id)
        except Exception as e:
            if type(e).__name__ == 'DuplicateKeyError':
                print('Error: A document with these properties already exists')
            else:
                print(f'An error occurred creating a document with url {self.url}', e)
            return False
        if self._id and self.term_frequencies:
            self.create_term_matrix()

        return True

    def update_document(self):
        """
        Updates the relevant document in the database.

        :return: bool
        """
        try:
            documents.update_one({"_id": self._id}, {"$set": self.info_db()})
            return True
        except Exception as e:
            print(f'Document with id {self._id} could not be updated', e)
            return False

    def create_term_matrix(self):
        """
        Creates a term-matrix for the document and updates the database record with it.

        :return: bool
        """
        try:
            self.term_matrix = pd.DataFrame(self.term_frequencies, index=[str(self._id), ])
            self.update_document()
            return True
        except Exception as e:
            print('Error:', e)
            return False
