import numpy as np
import random
import csv
from db.services_pymongo import documents
from scipy.sparse import csr_matrix
from tqdm import tqdm

'''
WARNING: When using a large number of documents, this script has a long runtime.
This is due to the function scipy.sparse.csr_matrix.
With n_docs = 500 it runs in ~6 minutes.
With n_docs = 5000 it runs in ~1 hour.
'''


# Generate a random sample of n_docs documents from the database.
n_docs = 5000
docs = random.sample(list(documents.find({}, {"_id": 0, "tf_text": 1})), n_docs)
tf_text_list = [list(tf_text_dict.values())[0] for tf_text_dict in docs]

# docs_list, doc_lens and tokens_list are the derived objects from which the stopword list will be built.
docs_list = list()
for tf_text in tf_text_list:
    docs_list.append(tf_text.split())

doc_lens = [len(doc) for doc in docs_list]
tokens_list = [token for doc in docs_list for token in doc]


# CREATE A DOCUMENT-TERM MATRIX


def csr_doc_term_matrix(list_docs):
    """
    Makes a sparse document-term matrix from a list of documents.
    INPUT: Each document in list_docs is a list of tokens (strings).

    OUTPUTS:
    - doc_term_matrix : A collection of (<term_id>, <document_id>) <frequency>
        For an entry '(i,j) frequency' frequency is the number of occurrences of term i in document j.
    - dict_term_id : a mapping of vocabulary terms to indices id=0,...,V-1
    """

    # Alphabetical vocab set and dictionary to store term ids
    vocab_set = set(tokens_list)
    vocab_sorted = sorted(list(vocab_set))
    V = len(vocab_sorted)
    dict_term_id = dict(zip(vocab_sorted, range(V)))

    D = len(list_docs)

    # Forming the csr_matrix function arguments
    rows = []
    cols = []
    data = []

    for i_doc in tqdm(range(D)):
        doc = list_docs[i_doc]
        data = data + [1] * len(doc)
        cols = cols + [i_doc] * len(doc)
        rows = rows + [dict_term_id[h] for h in doc]

    doc_term_matrix = csr_matrix((data, (rows, cols)), shape=(V, D), dtype=np.int64, copy=False)

    return doc_term_matrix, dict_term_id


doc_term_matrix, dict_term_id = csr_doc_term_matrix(docs_list)

# CALCULATE CONDITIONAL ENTROPY OF TERMS GIVEN A COLLECTION


def conditional_entropy_csr(sparse_matrix):
    """
    Calculates conditional entropy of each term from a csr sparse matrix representation of the term-document matrix.

    INPUT: csr_matrix
    OUTPUT: H_vector - numpy array of conditional entropies for each term in alphanumerical order
    """

    # Frequency of each term in the collection
    term_freq = np.array(sparse_matrix.sum(axis=1).transpose())[0]

    # Intermediate calculation
    n = sparse_matrix.data
    summand = n * np.log2(n)

    # Returns indices of summand where the entry is greater than 0
    # We keep only this information for efficient entropy calculations
    non_zero_summand_id = np.where(summand > 0)

    # Make a new csr_matrix using the entropy summand entries and their indices
    # but with the same dimensions as the initial matrix.

    # Row indices and column indices where the entries of the null sparse matrix are nonzero.
    # When paired elementwise, this gives the coordinates of non-zero elements of the term-document matrix.
    rows, cols = sparse_matrix.nonzero()

    # Grab only the non-zero elements of entropy summand, as well as their coordinates in the sparse matrix.
    row_H = rows[non_zero_summand_id]
    col_H = cols[non_zero_summand_id]
    data_H = summand[non_zero_summand_id]

    # Form a new (sparser) matrix of entropy summands
    entropy_matrix = csr_matrix((data_H, (row_H, col_H)), shape=sparse_matrix.shape)

    # Finish conditional entropy calculation
    H_vector = -np.array(entropy_matrix.sum(axis=1).transpose())[0] / term_freq + np.log2(term_freq)

    return H_vector


H_vector = conditional_entropy_csr(doc_term_matrix)


# COMPARISON WITH AVERAGE NULL MODEL


def shuffle_terms(doc_lens, tokens_list):
    """
    Shuffles tokens and redistributes them over the documents
    Returns a new document list with the terms shuffled
    Document lengths are preserved but terms are permuted across the entire collection
    """

    null_tokens = list(np.random.permutation(tokens_list))
    null_documents = list()
    start = 0

    for i in doc_lens:
        null_documents.append(null_tokens[start:start + i])
        start += i

    return null_documents


null_docs = shuffle_terms(doc_lens, tokens_list)


def null_model_generator(doc_lens, tokens_list):
    """
    Generates one iteration of the null model as follows:
    - Shuffles the tokens across the documents
    - Creates document-term matrix
    - Calculates the conditional entropy
    - Returns numpy array of conditional entropies
    """

    null_matrix, dict_term_id = csr_doc_term_matrix(shuffle_terms(doc_lens, tokens_list))

    return conditional_entropy_csr(null_matrix)


def null_model_iterator(n, doc_lens, tokens_list):
    """
    Iterates null_model_generator n times and takes the mean of the resulting H_vectors
    """

    null_sum = null_model_generator(doc_lens, tokens_list)

    for i in range(n-1):
        null_sum += null_model_generator(doc_lens, tokens_list)

    return null_sum/n


H_null_mean = null_model_iterator(10, doc_lens, tokens_list)

info_content = H_null_mean - H_vector


def get_stopword_list(threshold, info_content, dict_term_id):
    """
    All terms with absolute information content below threshold are put into the stopword list.
    Stores the inferred stopword list as inferred_stopwords.csv
    Overwrites an existing csv of the same name if function has been previously called.
    """

    inferred_stopword_indices = np.where(np.abs(info_content) < threshold)[0]

    inferred_stopword_list = list()

    for key, value in dict_term_id.items():
        if value in inferred_stopword_indices:
            inferred_stopword_list.append(key)

    with open('inferred_stopwords.csv', 'w+') as f:

        writer = csv.writer(f)
        writer.writerow(inferred_stopword_list)

    return


get_stopword_list(0.1, info_content, dict_term_id)
