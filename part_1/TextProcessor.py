import requests
from bs4 import BeautifulSoup
from nltk import word_tokenize
from nltk.stem import PorterStemmer
import collections

class TextProcessor:

    # Class constructor
    def __init__(self):
        self.stemmer = PorterStemmer()
        return

    def fetch(self, url):

        res = requests.get(url)
        soup = BeautifulSoup(res.text, "lxml")
        for s in soup(['script', 'style']):
            s.decompose()
        tokens = word_tokenize(' '.join(soup.stripped_strings))

        return tokens, soup.title.string

    def lower(self, tokens):
        return list(map(str.lower, tokens))

    def stem(self, tokens):
        return list(map(self.stemmer.stem, tokens))

    def getTerms(self, tokens):
        counts = collections.Counter(tokens)
        sortedList = sorted(tokens, key=counts.get, reverse=True)
        return list(set(sortedList))

t = TextProcessor()
tokens, title= t.fetch('https://www.wired.com/2004/10/tail/')
print(title)
print('Number of Tokens: ' + str(len(tokens)))
terms = t.getTerms(tokens)
print('Number of Terms: ' + str(len(terms)))
lowerTerms = t.getTerms(t.lower(tokens))
print('Number of Terms after lowercase: ' + str(len(lowerTerms)))
stemmedTokens = t.getTerms(t.stem(tokens))
print('Number of Terms after Porter Stemmer: ' + str(len(stemmedTokens)))