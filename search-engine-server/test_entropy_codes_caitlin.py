import pandas as pd
import numpy as np
from db import get_clinical_td_matrix
import os, sys
from scipy.sparse import csr_matrix
# import matplotlib.pyplot as plt

td = get_clinical_td_matrix()  # gets data from clinicaltrials.gov.pkl
td_matrix = td.matrix  # the document matrix
print(f'Shape = {td_matrix.shape}')


'''try 100 documents first'''
matrix_100 = td_matrix.iloc[:100, :100]
matrix_100 = matrix_100.fillna(0)
matrix_100 = matrix_100.astype(int)
# print(matrix_100.info())

from db.services_pymongo import documents

# returns all the documents from the database. specify num of docs in limit()
docs = list(documents.find({}, {"_id": 0, "clinical_id": 1, "term_frequencies": 1}).limit(100))

'''ENTROPY CODES TESTING'''


#  First step of conditional entropy calculation
def normalise(row):
    return row / row.sum()


df_term_distributions = matrix_100.apply(normalise, axis=0)
# print(df_term_distributions)


# Second step of conditional entropy calculation
def conditional_entropy_summand(row):
    result = []
    for x in row:
        if x != 0:
            result.append(-x * np.log2(x))
        else:
            result.append(0)
    return pd.Series(result)


# Putting the conditional entropy steps together and summing
def conditional_entropy(df):
    return df.apply(normalise, axis=0).apply(conditional_entropy_summand, axis=0).sum(axis=0)


df_conditional_entropy = conditional_entropy(matrix_100)
# print(df_conditional_entropy)


# Class objects
doc_lens = matrix_100.sum(axis=1)
tokens = [item['term_frequencies'].keys() for item in docs]
tokens_list = [key for sublist in tokens for key in sublist]  # returns a list of all the terms in the documents
# print(tokens_list)


def shuffle_terms(doc_lens, tokens_list):
    # shuffles tokens over the documents
    # returns a new document list with the terms shuffled
    null_tokens = list(np.random.permutation(tokens_list))
    null_documents = list()
    start = 0

    for i in doc_lens:
        null_documents.append(null_tokens[start:start + i])
        start += i

    return null_documents


null_docs = shuffle_terms(doc_lens, tokens_list)
# print(null_docs)

# Create a document-term matrix for the null document set
def null_csr(list_docs):
    '''
    Makes a sparse term-document matrix from a list of documents.
    Each document is a list of tokens (strings).
    Provides dict_term_id, a mapping of vocabulary terms to indices id=0,...,V-1

    term_doc_matrix : (word in number, document number) number on the right side is the frequency of words
    dict_term_id : dictionary of words to numbers
    '''

    # Alphabetical vocab set and dictionary to store term ids
    vocab_set = set(tokens_list)
    vocab_sorted = sorted(list(vocab_set))
    V = len(vocab_sorted)
    dict_term_id = dict(zip(vocab_sorted, range(V)))

    D = len(list_docs)

    # Creating the csr_matrix function arguments
    rows = []
    cols = []
    data = []

    for i_doc, doc in enumerate(list_docs):
        data += [1] * len(doc)
        cols += [i_doc] * len(doc)
        rows += [dict_term_id[h] for h in doc]

    term_doc_matrix = csr_matrix((data, (rows, cols)), shape=(V, D), dtype=np.int64, copy=False)
    return term_doc_matrix, dict_term_id
#
term_doc_matrix, dict_term_id = null_csr(null_docs)


def conditional_entropy_csr(sparse_matrix):
    '''
    Calculates conditional entropy of each term from a csr sparse matrix representation of the term-document matrix.
    Used to compute conditional entropy for the null model.

    INPUT: csr_matrix
    OUTPUT: numpy array of conditional entropies for each term in alphabetical order
    '''

    # Frequency of each term in the collection
    term_freq = np.array(sparse_matrix.sum(axis=1).transpose())[0]

    # Intermediate calculation
    n = sparse_matrix.data
    summand = n * np.log2(n)

    # Returns indices of summand where the entry is greater than 0
    # We only keep this information for entropy calculations
    non_zero_summand_id = np.where(summand > 0)

    ## Make a new csr_matrix using the entropy summand entries and their indices

    # Row indices and column indices where the entries of the null sparse matrix are nonzero.
    # When paired elementwise, this gives the coordinates of non-zero elements of the term-document matrix (for the null model).
    rows, cols = sparse_matrix.nonzero()

    # Grab only the non-zero elements of entropy summand, as well as their coordinates in the sparse matrix.
    row_H = rows[non_zero_summand_id]
    col_H = cols[non_zero_summand_id]
    data_H = summand[non_zero_summand_id]

    # Form a new (sparser) matrix of entropy summands
    entropy_matrix = csr_matrix((data_H, (row_H, col_H)), shape=sparse_matrix.shape)

    # Finish conditional entropy calculation
    H_null = -np.array(entropy_matrix.sum(axis=1).transpose())[0] / term_freq + np.log2(term_freq)

    return H_null

H_null =conditional_entropy_csr(term_doc_matrix)
# print(H_null)

# Shuffle (1000 times) and average the entropies

def null_model_generator(doc_lens, tokens_list):
    # Shuffle the tokens across the documents
    # Create document-term matrix
    # Calculate the conditional entropy
    # Returns numpy array of conditional entropy of terms
    null_matrix, dict_term_id = null_csr(shuffle_terms(doc_lens,tokens_list))
    return conditional_entropy_csr(null_matrix)

def null_model_iterator(n, doc_lens, tokens_list):
    # Iterates the null_model_generator n times and takes the mean of the results
    null_sum = null_model_generator(doc_lens,tokens_list)
    for i in range(n-1):
        null_sum += null_model_generator(doc_lens,tokens_list)
    return null_sum/n

null_mean = null_model_iterator(100, doc_lens, tokens_list)
print(null_mean)
#
# info_content = null_mean - df_conditional_entropy
# print(info_content)

# Distribution of information content of terms
# plt.hist(info_content)
# plt.xlabel("Information Content")
# plt.ylabel("Frequency")
# plt.show()

# Select a threshold. All terms with information content below the threshold are put into the stopword list.
# threshold = 0.1
# inferred_stopword_list = list(info_content.loc[np.abs(info_content)<threshold].index)
# print(inferred_stopword_list)
