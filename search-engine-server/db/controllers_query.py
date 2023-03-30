from bs4 import BeautifulSoup
from db.models_query import Query
from db.services_pymongo import documents
import re


def get_queries_by_clinical_id(ids: list):
    """
    Takes a list of clinical ids and returns the database _ids for relevant documents

    :param ids: list
    :return: list
    """
    return list(documents.find({"clinical_id": {"$in": ids}}, {"_id": 1}))


def relevance_parser(relevance_filepath: str):
    """
    Takes the Text Retrieval Conference clinical dataset relevancy list and returns a dictionary with labeled
    information.

    :param relevance_filepath: str
    :return: dict
    """
    with open(relevance_filepath, "r") as f:
        data = f.readlines()
    relevancy_data = list()
    for line in data:
        entry = line.split()
        relevancy_data.append({"topic_number": entry[0], "clinical_id": entry[2], "score": int(entry[3])})
    return relevancy_data


def process_query(relevance_filepath: str, query_filepath: str):
    """
    Takes the path of the Text Retrieval Conference clinical dataset relevancy and query lists.
    Creates database entries for each query.

    :param relevance_filepath: str
    :param query_filepath: str
    :return: None
    """
    relevancy = relevance_parser(relevance_filepath)
    with open(query_filepath, "r") as f:
        file = f.read()
    soup = BeautifulSoup(file, 'lxml')
    topics = soup.find_all('topic')
    for index, topic in enumerate(topics):
        print(f'processing query {index + 1} / {len(topics)} || {round(100 / len(topics) * (index + 1))}%')
        if match := re.search(r'<topic number=\"([0-9]+)\"', topic.__str__()):
            topic_number = match.group(1)
        else:
            continue
        trials = list(filter(lambda x: x['topic_number'] == topic_number, relevancy))
        trials_non_relevant = list(map(lambda x: x['clinical_id'], filter(lambda x: x['score'] == 0, trials)))
        trials_excluded = list(map(lambda x: x['clinical_id'], filter(lambda x: x['score'] == 1, trials)))
        trials_relevant = list(map(lambda x: x['clinical_id'], filter(lambda x: x['score'] == 2, trials)))

        query = {
            "topic_number": topic_number,
            "content": topic.text.strip(),
            "docs_relevant": get_queries_by_clinical_id(trials_relevant),
            "docs_non_relevant": get_queries_by_clinical_id(trials_non_relevant),
            "docs_excluded": get_queries_by_clinical_id(trials_excluded),
        }

        q = Query(query)
        q.create_document()
    return
