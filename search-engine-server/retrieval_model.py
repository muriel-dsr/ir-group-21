from db import get_documents_for_indexing, get_documents_for_client_with_client_id
from stopwords import stopword_list


async def retrieval_model(query: str):
    """
    Processes query from user and returns relevant documents

    :param query: str
    :return: list(documents)
    """
    docs = get_documents_for_indexing()  # Provides a dataframe with 'clinical_id' as index;

    # Some Dragos magic happens and a list of client ids appears...

    results = ['NCT04008381', 'NCT04002674', 'NCT04004702', 'NCT04007809', 'NCT04004468', 'NCT04004897', 'NCT04001582',
               'NCT04006223', 'NCT04000412', 'NCT04006834']

    return await get_documents_for_client_with_client_id(results)



