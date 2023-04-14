import pandas as pd
import pyterrier as pt
import nltk
import os
import random
from db.services_pymongo import documents
from db import get_documents_for_indexing, get_documents_for_client_with_client_id
from stopwords import custom_stopword_list
from nltk import word_tokenize
from tqdm import tqdm

nltk.download('punk')


''' Indexing and evaluation of the search engine model '''

# First we need to add pip install python-terrier to the requirements.txt

pt.init()


# First we create the index

def custom_preprocess(text):
    custom_stopword = custom_stopword_list()
    toks = word_tokenize(text)  # tokenize
    toks = [t for t in toks if t.lower() not in custom_stopword]  # remove stop words
    return ' '.join(toks)  # combine toks back into a string


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


def indexing_custom():
    """
    Creates the index using the dynamic stopword list.
    """

    docs_custom = pd.read_csv('docs_custom.csv')

    index_dir = "./pd_index_custom_workaround"

    if os.path.isdir(index_dir):
        print(f"Loading existing index at {index_dir}")
        custom_index = pt.IndexFactory.of("./pd_index_custom_workaround/data.properties")
    else:
        print(f"Creating new index at {index_dir}")
        pd_indexer_custom = pt.DFIndexer(index_dir,
                                         stopwords=None)  # We do not remove any more stopwords as they were removed in the creation of the docs_custom dataframe, we only tokenizer and stem;
        custom_index = pd_indexer_custom.index(docs_custom['text'], docs_custom['docno'])

    return custom_index


def indexing_control():
    """
    Creates the control index, used for evaluation purposes
    """

    # custom_stopword = custom_stopword_list()

    docs = get_documents_for_indexing()  # Provides a dataframe with all documents and their clinical_id to index;
    docs.rename(columns={'clinical_id': 'docno', 'raw_text': 'text'}, inplace=True)

    index_dir = "./pd_index_control_workaround"

    if os.path.isdir(index_dir):
        print(f"Loading existing index at {index_dir}")
        control_index = pt.IndexFactory.of("./pd_index_control_workaround/data.properties")
    else:
        print(f"Creating new index at {index_dir}")
        pd_indexer_control = pt.DFIndexer(index_dir, stopwords=None)  # Creates the custom indexer;
        control_index = pd_indexer_control.index(docs['text'], docs['docno'])

    return control_index


custom_index = indexing_custom()  # Creates the index that will be used in the BM-25 retrieval model
control_index = indexing_control()  # Created the control index


async def retrieval_model_custom(query: str):
    """
    Processes query from user and returns relevant documents

    :param query: str
    :return: list(documents)
    """

    bm25_dynamic = pt.BatchRetrieve(custom_index, wmodel="BM25",
                                    num_results=1000)  # Here we create the retrieval BM25 retrieval model;
    res_dynamic = bm25_dynamic.transform(
        query)  # Here our documents are scored based on the BM25 model and the input query;

    results = res_dynamic.loc[0:19,
              'docno'].tolist()  # Returns a list with the clinical_ids of the first 20 documents that scored the highest;

    return await get_documents_for_client_with_client_id(results)


async def retrieval_model_control(query: str):
    """
    Processes query from user and returns relevant documents

    :param query: str
    :return: list(documents)
    """

    bm25_dynamic = pt.BatchRetrieve(control_index, wmodel="BM25",
                                    num_results=1000)  # Here we create the retrieval BM25 retrieval model;
    res_dynamic = bm25_dynamic.transform(
        query)  # Here our documents are scored based on the BM25 model and the input query;

    results = res_dynamic.loc[0:19,
              'docno'].tolist()  # Returns a list with the clinical_ids of the first 20 documents that scored the highest;

    return await get_documents_for_client_with_client_id(results)


# Now we get the relevancy files and the topics

def evaluate():
    """
    Compare the results of using standard and custom stopword list

    :return: a table of evaluation metric results. The first row(0) is the values for standard stopwords
    """

    dataset = pt.get_dataset("irds:clinicaltrials/2021/trec-ct-2021")
    topics = dataset.get_topics()  # we get the topics in a format easy to use with the pyterrier evaluator framework
    qrels = dataset.get_qrels()  # we do the same with the relevancy files

    bm25_custom = pt.BatchRetrieve(custom_index, wmodel="BM25",
                                   num_results=1000)  # we create a bm-25 retrieval model that uses our custom list of stopwords
    bm25_control = pt.BatchRetrieve(control_index, wmodel="BM25",
                                    num_results=1000)  # now we create a model that we will use as control

    tf_idf_custom = pt.BatchRetrieve(custom_index, wmodel="TF_IDF", num_results=1000)

    # Dataframe to show us the different evaluation metrics on the standard and custom stopword list

    experiment = pt.Experiment([bm25_custom, bm25_control], topics, qrels,
                               ['map', 'P_5', 'recall_5', 'num_rel', 'num_rel_ret'])

    sum_p_r = experiment['P_5'] + experiment['recall_5']
    stopword_list = ['custom', 'standard']

    experiment.insert(0, 'stopword_list', stopword_list)
    experiment.insert(5, 'P+R', sum_p_r)

    # Dataframe of the evaluation metrics of BM25 and TF-IDF

    model_eval = pt.Experiment([bm25_custom, tf_idf_custom], topics, qrels,
                               ['ndcg', 'Rprec', 'num_rel', 'num_rel_ret'])

    pd.set_option('display.max_columns', None)

    return experiment, model_eval
