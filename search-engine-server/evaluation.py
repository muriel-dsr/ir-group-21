from retrieval_custom_preprocess import evaluate

''' Shows a table of the evaluation results '''

experiment, model_eval = evaluate()

print(f'\nStopword list comparison:\n\n{experiment}')
print(f'Retrieval model comparison:\n\n{model_eval}')