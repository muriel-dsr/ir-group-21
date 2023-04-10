import pyterrier as pt
from db import get_documents_for_indexing, get_documents_for_client_with_client_id
from stopwords import stopword_list, standard_stopword_list

# First we need to add pip install python-terrier to the requirements.txt

pt.init()

# First we create the index

def indexing_custom():
    """
    Creates the index using the dynamic stopword list.
    Currently using standard stopword list for testing purposes
    """

    standard_stopword = standard_stopword_list()  # nltk and sklear

    docs = get_documents_for_indexing()  # Provides a dataframe with all documents and their clinical_id to index;
    docs.rename(columns={'clinical_id': 'docno', 'raw_text': 'text'}, inplace=True)

    pd_indexer_custom = pt.DFIndexer("./pd_index_custom", stopwords=standard_stopword) # Creates the custom indexer;
    custom_index = pd_indexer_custom.index(docs['text'], docs['docno'])

    return custom_index


def indexing_control():
    """
    Creates the control index, used for evaluation purposes
    """

    docs = get_documents_for_indexing()  # Provides a dataframe with all documents and their clinical_id to index;
    docs.rename(columns={'clinical_id': 'docno', 'raw_text': 'text'}, inplace=True)

    pd_indexer_control = pt.DFIndexer("./pd_index_control")  # Creates the control indexer;
    control_index = pd_indexer_control.index(docs['text'], docs['docno'])

    return control_index

custom_index = indexing_custom()  # Creates the index that will be used in the BM-25 retrieval model


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

    results = res_dynamic.loc[0:19, 'docno'].tolist()  # Returns a list with the clinical_ids of the first 20 documents that scored the highest;

    return await get_documents_for_client_with_client_id(results)
