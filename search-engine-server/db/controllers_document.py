from bs4 import BeautifulSoup
from db.models_document import Document
from textanalyser import list_words
import re


def get_soup_text(soup: BeautifulSoup, tag: str):
    """
    Takes an instance of BeautifulSoup and checks whether a tag is present. Returns the tag text or None.

    :param soup: BeautifulSoup
    :param tag: str
    :return: str | None
    """
    try:
        text = soup.find(tag).get_text()
        return text
    except AttributeError:
        return None


def find_domain(url: str):
    """
    Takes a URL str and returns the domain substring.

    :param url: str
    :return: str
    """
    if url is None:
        return None
    if match := re.search(r"//([a-zA-Z.]+)/", url):
        return match.group(1)
    elif match := re.search(r"//([a-zA-Z.]+)$", url):
        return match.group(1)


def process_clinical_trial(path: str):
    """
    Process an individual sample from the dataset and add it to the database. Returns an instance of the Document class.

    :param path: str: the path of the xml file
    :return: Document:
    """
    try:
        with open(path) as f:
            file = f.read()
    except FileNotFoundError:
        print(f'Error: file {path} could not be processed')
        return
    data = dict()
    soup = BeautifulSoup(file, 'lxml')

    data['title'] = get_soup_text(soup, 'brief_title')
    data['url'] = get_soup_text(soup, 'url')
    data['domain'] = find_domain(data['url'])
    if get_soup_text(soup, 'brief_summary'):
        data['description'] = get_soup_text(soup, 'brief_summary').replace('\r\n     ', '').strip()
    else:
        data['description'] = None
    data['term_frequencies'] = list_words(soup.text)['all']

    doc = Document(data)

    doc.create_document()

    return doc
