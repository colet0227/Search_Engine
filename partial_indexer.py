import json
import os
from collections import defaultdict
from bs4 import BeautifulSoup
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer

class PartialIndexer:
    def __init__(self, max_size=5 * 1024 * 1024):  # 5MB in bytes
        self.stemmer = PorterStemmer()

        # The keys of self.index will be the tokens
        self.index = defaultdict(lambda: {'freq': 0, 'docs': set(), 'importance': defaultdict(int)})
        self.important_tags = ['b', 'strong', 'h1', 'h2', 'h3', 'title']
        self.current_size = 0
        self.max_size = max_size

    def tokenize_and_stem(self, text):
        tokens = word_tokenize(text)

        # Use PorterStemmer to stem token before adding
        return [self.stemmer.stem(token) for token in tokens]

    def add_document(self, document, doc_id):
        soup = BeautifulSoup(document, 'html.parser')

        # Tokenize and add all text in the document
        all_text = soup.get_text()
        tokens = self.tokenize_and_stem(all_text)
        for token in tokens:
            self.index[token]['freq'] += 1
            self.index[token]['docs'].add(doc_id)
            self.index[token]['importance'][doc_id] += 1

        # Find the important tags, tokenize their text, and increment the importance of those tokens
        for tag in soup.find_all(self.important_tags):
            important_tokens = self.tokenize_and_stem(tag.get_text())
            for token in important_tokens:
                self.index[token]['importance'][doc_id] += 1

    def should_write_partial_index(self):
        # In a real implementation, replace with actual memory usage of self.index
        return self.current_size >= self.max_size

    def write_partial_index(self, path):
        with open(path, 'w') as f:
            # Convert sets to lists for JSON serialization
            index = {k: {ik: list(iv) if isinstance(iv, set) else iv for ik, iv in v.items()} for k, v in self.index.items()}
            json.dump(index, f)
        self.current_size = 0
        self.index.clear()


if __name__ == "__main__":
    partial_indexer = PartialIndexer()

    root_dir = "/Users/colethompson/Documents/A3/DEV"  # Root directory path
    file_paths = []  # This list will contain the paths of all JSON files

    # Traverse through all subdirectories
    for dir_path, _, filenames in os.walk(root_dir):
        for file in filenames:
            if file.endswith(".json"):  # If the file is a JSON file
                file_paths.append(os.path.join(dir_path, file))  # Add its path to the list

    partial_index_count = 0
    for path in file_paths:
        with open(path, 'r') as file:
            data = json.load(file)
            partial_indexer.add_document(data['content'], data['url'])
            if partial_indexer.should_write_partial_index():
                partial_indexer.write_partial_index(f'partial_index_{partial_index_count}.json')
                partial_index_count += 1
