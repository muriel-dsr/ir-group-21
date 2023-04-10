from sklearn.feature_extraction._stop_words import ENGLISH_STOP_WORDS
from nltk.corpus import stopwords

def stopword_list():
    """ Returns a stopword list"""

    # Some Caitlin magic happens and a list of stopwords appears...

    return ['fandabidosy']

def standard_stopword_list():
    ''' Returns the combined stopword list from NLTK and Scikitlearn '''

    nltk_stopword = stopwords.words('english')
    sklearn_stopword = ENGLISH_STOP_WORDS

    combined_stopword = set(nltk_stopword).union(set(sklearn_stopword))

    return combined_stopword
