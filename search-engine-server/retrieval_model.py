import pyterrier as pt
import os
from db import get_documents_for_indexing, get_documents_for_client_with_client_id
from stopwords import standard_stopword_list, custom_stopword_list

# First we need to add pip install python-terrier to the requirements.txt

pt.init()


# First we create the index

def indexing_custom():
    """
    Creates the index using the dynamic stopword list.
    Currently using standard stopword list for testing purposes
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



# Now we get the relevancy files and the topics

def evaluate():
    dataset = pt.get_dataset("irds:clinicaltrials/2021/trec-ct-2021")
    topics = dataset.get_topics()  # we get the topics in a format easy to use with the pyterrier evaluator framework
    qrels = dataset.get_qrels()  # we do the same with the relevancy files

    bm25_custom = pt.BatchRetrieve(custom_index, wmodel="BM25",
                                   num_results=1000)  # we create a bm-25 retrieval model that uses our custom list of stopwords
    bm25_control = pt.BatchRetrieve(control_index, wmodel="BM25",
                                    num_results=1000)  # now we create a model that we will use as control

    # Here we create a pandas df that will show us the different evaluation metrics on the two models

    experiment = pt.Experiment([bm25_custom, bm25_control], topics, qrels, ['map', 'ndcg', 'P_5', 'recall_5'])
    experiment['sum'] = experiment['P_5'] + experiment['recall_5']

    return experiment
