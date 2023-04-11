from db.services_pymongo import documents, queries, create_all_indexes
from db.models_document import Document
from db.controllers_document import process_clinical_trial, get_documents_for_matrix, get_documents_terms
from db.controllers_document import get_documents_for_indexing, get_documents_for_client_with_client_id
from db.controllers_document import get_documents_for_stop_list
from db.controllers_tdmatrix import get_clinical_td_matrix
from db.controllers_query import process_query, get_query_list_for_client

# line 3 : get_document_matrix is a new addition from Muriel
