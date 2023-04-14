import pandas as pd
import pyterrier as pt
import os
from db import get_documents_for_indexing, get_documents_for_client_with_client_id
from stopwords import standard_stopword_list, custom_stopword_list

''' Indexing and evaluation of the search engine model '''

#  Initialise PyTerrier
pt.init()


def indexing_custom():
    """
    Creates the index using the dynamic stopword list.
    """

    custom_stopword = custom_stopword_list()

    docs = get_documents_for_indexing()  # Provides a dataframe with all documents and their clinical_id to index;
    docs.rename(columns={'clinical_id': 'docno', 'raw_text': 'text'}, inplace=True)

    index_dir = "./pd_index_custom"

    if os.path.isdir(index_dir):
        print(f"Loading existing index at {index_dir}")
        custom_index = pt.IndexFactory.of("./pd_index_custom/data.properties")
    else:
        print(f"Creating new index at {index_dir}")
        pd_indexer_custom = pt.DFIndexer(index_dir, stopwords=custom_stopword)  # Creates the custom indexer;
        custom_index = pd_indexer_custom.index(docs['text'], docs['docno'])

    return custom_index


def indexing_control():
    """
    Creates the control index, used for evaluation purposes
    """

    standard_stopword = standard_stopword_list()  # nltk and sklear

    docs = get_documents_for_indexing()  # Provides a dataframe with all documents and their clinical_id to index;
    docs.rename(columns={'clinical_id': 'docno', 'raw_text': 'text'}, inplace=True)

    index_dir = "./pd_index_control"

    if os.path.isdir(index_dir):
        print(f"Loading existing index at {index_dir}")
        control_index = pt.IndexFactory.of("./pd_index_control/data.properties")
    else:
        print(f"Creating new index at {index_dir}")
        pd_indexer_control = pt.DFIndexer(index_dir, stopwords=standard_stopword)  # Creates the custom indexer;
        control_index = pd_indexer_control.index(docs['text'], docs['docno'])

    return control_index


custom_index = indexing_custom()  # Creates the index that will be used in the BM-25 retrieval model
control_index = indexing_control()  # Created the control index


async def retrieval_model(query: str):
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
    stopword_list = ['standard', 'custom']

    experiment.insert(0, 'stopword_list', stopword_list)
    experiment.insert(5, 'P+R', sum_p_r)

    # Dataframe of the evaluation metrics of BM25 and TF-IDF

    model_eval = pt.Experiment([bm25_custom, tf_idf_custom], topics, qrels,
                               ['ndcg', 'Rprec', 'num_rel', 'num_rel_ret'])

    pd.set_option('display.max_columns', None)

    return experiment, model_eval
