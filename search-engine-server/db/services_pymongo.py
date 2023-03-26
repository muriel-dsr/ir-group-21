from pymongo import MongoClient, ASCENDING

# Connect to mongoDB
client = MongoClient('mongodb://localhost:27017/')

# Connect to specific database
db = client.ir_group_21_clinical

# Connect to specific collection in database
documents = db.documents


def create_indexes(collection, attribute):
    """Create indexes to ensure that no duplicates are added to database"""
    return collection.create_index([(attribute, ASCENDING)], unique=True)


create_indexes(documents, 'url')
