from retrieval_model import indexing_control

# We create our control index

control_index = indexing_control()

# Now we get the relevancy files and the topics

def evaluate():

    dataset = pt.get_dataset("irds:clinicaltrials/2021/trec-ct-2021")
    topics = dataset.get_topics() # we get the topics in a format easy to use with the pyterrier evaluator framework
    qrels = dataset.get_qrels() # we do the same with the relevancy files

    bm25_custom = pt.BatchRetrieve(custom_index, wmodel="BM25", num_results=1000) # we create a bm-25 retrieval model that uses our custom list of stopwords
    bm25_control = pt.BatchRetrieve(control_index, wmodel="BM25", num_results=1000) # now we create a model that we will use as control

    # Here we create a pandas df that will show us the different evaluation metrics on the two models

    experiment = pt.Experiment( [bm25_custom, bm25_control], topics, qrels, ['map', 'ndcg', 'P_5', 'recall_5'])
    experiment['sum'] = experiment['P_5'] + experiment['recall_5']

    return experiment

evaluation_df = evaluate()

