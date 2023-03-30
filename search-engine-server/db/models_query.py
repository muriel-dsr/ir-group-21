from bson.objectid import ObjectId
from db.services_pymongo import queries


class Query:
    """
    This class contains all the information relevant to the query including relevance documents for the judgement.

    Attributes

    _id: ObjectId | str | None - database id for the query

    topic_number: int | None - topic number provided by trec clinical dataset

    content: str | None - content of the query

    docs_relevant: list | None - list of _ids for database documents relevant to the query

    docs_non_relevant: list | None - list of _ids for database documents NOT relevant to the query

    docs_excluded: list | None - list of _ids for database documents excluded from the query

    Methods

    info: dict - return all class variables as a dictionary

    info_db: dict - return all class variables for creating / updating the database

    create_document: bool - adds the document to the database

    update_document: bool - updates the relevant document in the database.

    """

    def __init__(self, doc: dict = None):
        """
        Initialise all variables in class and generate variables that rely on others.
        """
        self._id: ObjectId | str | None = None
        self.topic_number: int | None = None
        self.content: str | None = None
        self.docs_relevant: list | None = None
        self.docs_non_relevant: list | None = None
        self.docs_excluded: list | None = None

        # If document exists assign each value pair to the respective value pair for class instance
        if doc:
            for k, v in doc.items():
                setattr(self, k, v)

    def info(self):
        """
        Return all class variables as a dictionary.

        :return: dict
        """
        return {
            "_id": self._id,
            "topic_number": self.topic_number,
            "content": self.content,
            "docs_relevant": self.docs_relevant,
            "docs_non_relevant": self.docs_non_relevant,
            "docs_excluded": self.docs_excluded
        }

    def info_db(self):
        """
         Return all class variables (excluding self._id) as a dict for the purpose of creating / updating the database

        :return: dict
        """
        info = self.info()
        del info["_id"]
        return info

    def create_document(self):
        """
        Adds the document to the database.

        :return: bool
        """
        try:
            inserted = queries.insert_one(self.info_db())
            self._id = ObjectId(inserted.inserted_id)
        except Exception as e:
            if type(e).__name__ == 'DuplicateKeyError':
                print('Error: A document with these properties already exists')
            else:
                print(f'An error occurred creating a document with topic number {self.topic_number}', e)
            return False
        return True

    def update_document(self):
        """
        Updates the relevant document in the database.

        :return: bool
        """
        try:
            queries.update_one({"_id": self._id}, {"$set": self.info_db()})
            return True
        except Exception as e:
            print(f'Document with id {self._id} could not be updated', e)
            return False
