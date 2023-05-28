import csv
import re
import sys
import json
from collections import defaultdict
from bs4 import BeautifulSoup
from nltk.stem import SnowballStemmer

class PartialIndexer:
    def __init__(self):
        # Stemmer from nltk library - test with PorterStemmer too
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

        self.HTML_WEIGHTS = {
            # Title added additional weight because of extreme importance
            'title': 25, 

            # Headers
            'h1': 10,
            'h2': 9,
            'h3': 7,
            'h4': 4,
            'h5': 2,
            'h6': 1,

            # Bold
            'b': 3,
            'strong': 3,

            # Italic
            'i': 2,
            'em': 2
        }

        # Current size of index
        self.current_size = 0

        # Max size before we create a partial index
        self.max_size = 5242880 # 5mb

        # Unique doc id we increment (hash value)
        self.id_counter = 1

        # URL to unique ID map
        # Useful to first check if url already has an assigned id without having to check file
        self.url_id_map = {}

    def tokenize_and_stem(self, text):
        # Use regex expression
        tokens = re.findall(r'\b[a-zA-Z0-9]+\b', text)

        # Lower and stem before returning list of tokens
        return [self.stemmer.stem(token.lower()) for token in tokens]

    def add_document(self, document, document_url, url_id_map_path):
        # Generate ID for the document
        id = self.get_id(document_url)

        # Parse the document
        soup = BeautifulSoup(document, 'html.parser')

        # Add the document URL and its ID to the URL-ID csv file
        self.add_url_to_map(document_url, id, url_id_map_path)

        # Get all the text in the url and tokenize
        all_text = soup.get_text()
        tokens = self.tokenize_and_stem(all_text)

        for token in tokens:
            # If this is the first occurrence of the token, initialize its entry in the index
            if token not in self.index:
                self.index[token] = {'token_freq': 0, 'document_freq': 0, 'doc_ids': defaultdict(lambda: {'id': id, 'freq': 0, 'weight': 0, 'tf_idf': 0})}

            # Increase the total frequency of the token
            self.index[token]['token_freq'] += 1

            # If this is the first occurrence of the token in this document, initialize its entry in doc_ids and increase the document frequency
            if id not in self.index[token]['doc_ids']:
                self.index[token]['document_freq'] += 1
                self.index[token]['doc_ids'][id] = {'id': id, 'freq': 1, 'weight': 0, 'tf_idf': 0}
            else:
                # Otherwise, just increase the frequency of the token in this document
                self.index[token]['doc_ids'][id]['freq'] += 1

        # Process each HTML tag in the document
        for tag in soup.find_all():
            # Get the weight of the tag
            weight = self.HTML_WEIGHTS.get(tag.name, 1)

            # Tokenize and stem the text within the tag
            important_tokens = self.tokenize_and_stem(tag.get_text())

            for token in important_tokens:
                # If the token is in the index and its ID is in doc_ids, increase its weight
                if token in self.index and id in self.index[token]['doc_ids']:
                    self.index[token]['doc_ids'][id]['weight'] += weight

        # Update the current size of the index
        self.update_index_size()

        # Increase the current size by the size of the document
        self.current_size += len(document.encode('utf-8'))


    def should_write_partial_index(self):
        # If current size exceeds max size write a partial index
        return self.current_size >= self.max_size

    def update_index_size(self):
        # Update index size
        self.current_size = sys.getsizeof(self.index)

    def write_partial_index(self, path):
        # Write to a csv file
        with open(path, 'w', newline='') as csvfile:
            # Define the fields or columns in the CSV file
            fieldnames = ['Token', 'Data']

            # Create a CSV writer that writes dictionaries into the file and write header
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            # Iterate over each token in the index
            for token in sorted(self.index.keys()):
                # Write token index structure as shown above
                writer.writerow({'Token': token, 'Data': json.dumps(self.index[token])})

        # Reset current size and clear index dictionary (might free up memory idk)
        self.current_size = 0
        self.index.clear()

    def get_id(self, url):
        # Check if the URL is already in the url_id_map dictionary
        if url not in self.url_id_map:
            # If not, assign the current id_counter value to this URL in the dictionary
            self.url_id_map[url] = self.id_counter

            # Increment the id_counter for the next new URL's id value
            self.id_counter += 1
        
        # Return id
        return self.url_id_map[url]

    def add_url_to_map(self, url, id, filename):
        # APPEND to csv file
        with open(filename, mode='a', newline='', encoding='utf-8') as file:
            # Create a CSV writer object that will write into the file
            writer = csv.writer(file)

            # Write a new row into the CSV file with the id and the url
            writer.writerow([id, url])
