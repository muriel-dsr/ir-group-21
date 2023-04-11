import csv
from sklearn.feature_extraction._stop_words import ENGLISH_STOP_WORDS
from nltk.corpus import stopwords

def custom_stopword_list():
    """ Opens the csv file containing stopword list. Returns a list"""

    file = open("inferred_stopwords.csv", "r")
    data = list(csv.reader(file, delimiter=","))
    custom_stopword = data[0]

    return custom_stopword

def standard_stopword_list():
    """ Returns the combined stopword list from NLTK and Scikitlearn """

    nltk_stopword = stopwords.words('english')
    sklearn_stopword = ENGLISH_STOP_WORDS

    combined_stopword = set(nltk_stopword).union(set(sklearn_stopword))

    return combined_stopword

custom_stopword = custom_stopword_list()
print(type(custom_stopword))
