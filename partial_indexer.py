import re
import sys
import json
import math
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
            'title': 20,  # Title has highest weight
            'h1': 10, 'h2': 9, 'h3': 7, 'h4': 4, 'h5': 2, 'h6': 1,  # Headers
            'b': 3, 'strong': 3,  # Bold
            'i': 2, 'em': 2  # Italic
        }

        # Current size of index
        self.current_size = 0

        # Max size before we create a partial index
        self.max_size = 1000000 # 5242880 5b

        # Unique doc id we increment (hash value)
        self.id_counter = 1

        # URL to unique ID map
        self.url_id_map = {}

    def tokenize_and_stem(self, text):
        tokens = re.findall(r'[a-zA-Z0-9]+', text)
        return [self.stemmer.stem(token.lower()) for token in tokens]

    def add_document(self, document, document_url, url_id_map_path):
        document_url, _ = urldefrag(document_url)
        if document_url in self.url_id_map:
            return

        id = self.get_id(document_url)
        soup = BeautifulSoup(document, 'html.parser')

        self.add_url_to_map(document_url, id, url_id_map_path)

        all_text = soup.get_text()
        tokens = self.tokenize_and_stem(all_text)

        for token in tokens:
            self.index[token]['token_freq'] += 1
            if id not in self.index[token]['doc_ids']:
                self.index[token]['document_freq'] += 1
                self.index[token]['doc_ids'][id] = {'id': id, 'freq': 1, 'weight': 0}
            else:
                self.index[token]['doc_ids'][id]['freq'] += 1

        for tag in soup.find_all():
            weight = self.HTML_WEIGHTS.get(tag.name, 1)
            important_tokens = self.tokenize_and_stem(tag.get_text())

            for token in important_tokens:
                if token in self.index and id in self.index[token]['doc_ids']:
                    self.index[token]['doc_ids'][id]['weight'] += weight

        self.update_index_size()
        self.current_size += len(document.encode('utf-8'))


    def should_write_partial_index(self):
        return self.current_size >= self.max_size

    def update_index_size(self):
        self.current_size = sys.getsizeof(self.index)

    def write_partial_index(self, path):
        # with open(path, 'w') as txtfile:
        #     for token in sorted(self.index.keys()):
        #         txtfile.write(f'{token}: {json.dumps(self.index[token])}\n')

        # self.current_size = 0
        # self.index.clear()
        with open(path, 'w', newline='') as csvfile:
            fieldnames = ['token', 'data']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            writer.writeheader()
            for token in sorted(self.index.keys()):
                writer.writerow({'token': token, 'data': json.dumps(self.index[token])})

        self.current_size = 0
        self.index.clear()

    def get_id(self, url):
        if url not in self.url_id_map:
            self.url_id_map[url] = self.id_counter
            self.id_counter += 1
        return self.url_id_map[url]

    def add_url_to_map(self, url, id, filename):
        # with open(filename, mode='a', encoding='utf-8') as file:
        #     file.write(f'{id}:{url}\n')
        with open(filename, mode='a', newline='', encoding='utf-8') as csvfile:
            fieldnames = ['id', 'url']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

            if csvfile.tell() == 0:
                writer.writeheader()

            writer.writerow({'id': id, 'url': url})



