import re
import sys
import json
import csv
from collections import defaultdict
from bs4 import BeautifulSoup
from nltk.stem import SnowballStemmer
from urllib.parse import urldefrag

class PartialIndexer:
    def __init__(self):
        # Stemmer from nltk library
        self.stemmer = SnowballStemmer("english")

        # Structure of index
        self.index = defaultdict(lambda: {'token_freq': 0, 'document_freq': 0, 'doc_ids': defaultdict(lambda: {'id': '', 'freq': 0, 'weight': 0, 'tf_idf': 0})})
        # {
        #   "token": {
        #       "token_freq": 0,
        #       "document_freq": 0,
        #       "doc_ids": {
        #           "id": {
        #               "id": "",
        #               "token_freq": 0,
        #               "weight": 0,
        #               "tf_idf_score": 0,
        #           },
        #           "id": {
        #               "id": "",
        #               "token_freq": 0,
        #               "weight": 0,
        #               "tf_idf_score": 0,
        #           }
        #           etc...
        #       }
        #   }
        # }

        # Weights assigned to HTML tags
        self.HTML_WEIGHTS = {
            'title': 100,  # Title has highest weight
            'h1': 90, 'h2': 15, 'h3': 7, 'h4': 4, 'h5': 2, 'h6': 1,  # Headers
            'b': 3, 'strong': 3,  # Bold
            'i': 2, 'em': 2  # Italic
        }

        # Current size of index
        self.current_size = 0

        # Max size before we create a partial index
        self.max_size = 5242880 # 5mb

        # Unique doc id we increment (hash value)
        self.id_counter = 1

        # URL to unique ID map
        self.url_id_map = {}

    def tokenize_and_stem(self, text):
        tokens = re.findall(r'[a-zA-Z0-9]+', text)
        return [self.stemmer.stem(token.lower()) for token in tokens]

    def add_document(self, document, document_url, url_id_map_path):
        # Defrag document url
        document_url, _ = urldefrag(document_url)

        # Break if the URL is already in the url_id_map
        if document_url in self.url_id_map:
            return

        # Get or create an id for the document URL
        id = self.get_id(document_url)

        # Parse the document with BeautifulSoup
        soup = BeautifulSoup(document, 'html.parser')

        # Add the document URL to the url_id_map
        self.add_url_to_map(document_url, id, url_id_map_path)

        # Extract all text from the document and tokenize it
        all_text = soup.get_text()
        tokens = self.tokenize_and_stem(all_text)

        # Update the index with the tokens
        for token in tokens:
            self.index[token]['token_freq'] += 1
            if id not in self.index[token]['doc_ids']:
                self.index[token]['document_freq'] += 1
                self.index[token]['doc_ids'][id] = {'id': id, 'freq': 1, 'weight': 0}
            else:
                self.index[token]['doc_ids'][id]['freq'] += 1

        # Iterate over all HTML tags in the document and update weights
        for tag in soup.find_all():
            weight = self.HTML_WEIGHTS.get(tag.name, 1)
            important_tokens = self.tokenize_and_stem(tag.get_text())

            for token in important_tokens:
                if token in self.index and id in self.index[token]['doc_ids']:
                    self.index[token]['doc_ids'][id]['weight'] += weight

        # Update the current size of the index
        self.update_index_size()
        self.current_size += len(document.encode('utf-8'))


    def should_write_partial_index(self):
        # Check if the current size of the index exceeds the maximum size
        return self.current_size >= self.max_size

    def update_index_size(self):
        # Update the current size of the index
        self.current_size = sys.getsizeof(self.index)

    def write_partial_index(self, path):
        # Write the current index to a partial index file
        with open(path, 'w', newline='') as csvfile:
            fieldnames = ['token', 'data']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            for token in sorted(self.index.keys()):
                writer.writerow({'token': token, 'data': json.dumps(self.index[token])})

        # Reset the current size and clear the index
        self.current_size = 0
        self.index.clear()

    def get_id(self, url):
        # If the URL is not in the url_id_map, add it and increment the id_counter
        if url not in self.url_id_map:
            self.url_id_map[url] = self.id_counter
            self.id_counter += 1
        return self.url_id_map[url]

    def add_url_to_map(self, url, id, filename):
        # Add the URL and its id to the url_id_map file
        with open(filename, mode='a', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['id', 'url']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writerow({'id': id, 'url': url})



