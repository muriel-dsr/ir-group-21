import pyterrier as pt
from db import get_documents_for_indexing, get_documents_for_client_with_client_id
from stopwords import stopword_list

# First we need to add pip install python-terrier to the requirements.txt

pt.init()


async def retrieval_model(query: str):
    """
    Processes query from user and returns relevant documents

    :param query: str
    :return: list(documents)
    """
    docs = get_documents_for_indexing()  # Provides a dataframe with 'clinical_id' as index;
    docs.rename(columns={'clinical_id': 'docno', 'raw_text': 'text'}, inplace=True)

    # Here custom is the custom list of words
    pd_indexer_custom = pt.DFIndexer("./pd_index_custom", stopwords=custom)  # Creates the custom indexer;
    custom_index = pd_indexer_custom.index(docs['text'], docs['docno'])  # Indexes our documents;

    bm25_dynamic = pt.BatchRetrieve(custom_index, wmodel="BM25", num_results=1000)  # Here we create the retrieval BM25 retrieval model;
    res_dynamic = bm25_dynamic.transform(query)  # Here our documents are scored based on the BM25 model and the input query;

    results = res_dynamic.loc[0:20, 'docno'].tolist()  # Returns a list with the clinical_ids of the first 20 documents that scored the highest;

    return await get_documents_for_client_with_client_id(results)