import csv
import json
import time
import re
from nltk.stem import SnowballStemmer
from itertools import combinations

class IndexReader:
    def __init__(self, merged_index_path, secondary_index_path):
        self.secondary_index = self.load_secondary_index(secondary_index_path)
        self.index_file = open(merged_index_path, 'r')
        
    @staticmethod
    def load_secondary_index(secondary_index_path):
        secondary_index = {}
        with open(secondary_index_path, 'r') as f:
            reader = csv.reader(f)
            for token, offset in reader:
                secondary_index[token] = int(offset)
        return secondary_index

    def get_postings_list(self, token):
        line_start = self.secondary_index.get(token)
        if line_start is not None:
            self.index_file.seek(line_start)
            line = self.index_file.readline()
            row_token, row_data = line.strip().split(',', 1)
            if row_token == token:
                try:
                    # Remove extra double quotes around the json data
                    row_data = row_data.replace('""', '"')[1:-1]
                    return json.loads(row_data)
                except json.JSONDecodeError:
                    print(f"Error parsing JSON data: {row_data}")
        return None


stemmer = SnowballStemmer("english")
MERGED_PATH = '/Users/colethompson/Documents/A3/Updated/merged_index.csv'
SECONDARY_PATH = '/Users/colethompson/Documents/A3/Updated/secondary_index.csv'
MAPPING_PATH = '/Users/colethompson/Documents/A3/Updated/url_id_map.csv'
MAX_DOCS_PER_TOKEN = 10
WEIGHT_THRESHOLD = 0.1

def load_mapping(mapping_path):
    mapping = {}
    with open(mapping_path, 'r') as file:
        next(file)  # Skip the header
        reader = csv.reader(file, delimiter=',')
        for row in reader:
            if len(row) >= 2:
                mapping[row[0]] = row[1].strip()
            else:
                print(f"Skipping line due to wrong format: {row}")
    return mapping


def preprocess_query(query):
    words = re.findall(r'[a-zA-Z0-9]+', query)
    return [stemmer.stem(token.lower()) for token in words]

def get_docs(query_tokens, index_reader):
    return [set(list(index_reader.get_postings_list(token)['doc_ids'].keys())[:MAX_DOCS_PER_TOKEN]) for token in query_tokens if index_reader.get_postings_list(token) is not None]

def union_doc_lists(doc_lists):
    return set.union(*doc_lists) if doc_lists else set()

def calculate_scores(union_docs, query_tokens, index_reader):
    scores = {}
    for doc_id in union_docs:
        scores[doc_id] = sum(index_reader.get_postings_list(token)['doc_ids'].get(doc_id, {}).get('tf_idf', 0) for token in query_tokens if index_reader.get_postings_list(token) is not None)
        if scores[doc_id] < WEIGHT_THRESHOLD:
            del scores[doc_id]
    return scores

def rank_documents(scores, num_results=100):
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)[:num_results]

def search(query, index_reader, mapping, num_results=100):
    start_time = time.time()

    query_tokens = preprocess_query(query)
    union_docs = union_doc_lists(get_docs(query_tokens, index_reader))

    if len(union_docs) < num_results:
        for i in range(len(query_tokens)-1, 0, -1):
            for subset in combinations(query_tokens, i):
                subset_union_docs = union_doc_lists(get_docs(list(subset), index_reader))
                union_docs.update(subset_union_docs)
                if len(union_docs) >= num_results:
                    break
            if len(union_docs) >= num_results:
                break

    top_docs = rank_documents(calculate_scores(union_docs, query_tokens, index_reader), num_results)
    top_docs = [(mapping[doc_id], score) for doc_id, score in top_docs]

    print(f"Elapsed time: {(time.time() - start_time) * 1000} milliseconds")
    return top_docs

if __name__ == '__main__':
    index_reader = IndexReader(MERGED_PATH, SECONDARY_PATH)
    mapping = load_mapping(MAPPING_PATH)
    
    query = input("Search: ")
    print(search(query, index_reader, mapping))

    # with open(MERGED_PATH, 'r') as merged_index:
    #     merged_index.seek(2390243)  # Go to byte offset 3168
    #     line = merged_index.readline()  # Read the line at that position
    #     print(line)
