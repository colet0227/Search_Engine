import csv
import json
import time
import re
import heapq
import math
from nltk.stem import SnowballStemmer

K_DOCUMENTS = 10

class IndexReader:
    def __init__(self, merged_index_path, secondary_index_path):
        self.secondary_index = self.load_secondary_index(secondary_index_path)
        self.index_file = open(merged_index_path, 'r')

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
                    row_data = row_data.replace('""', '"')[1:-1]
                    return json.loads(row_data)
                except json.JSONDecodeError:
                    print(f"Error parsing JSON data: {row_data}")
        return None

stemmer = SnowballStemmer("english")
MERGED_PATH = '/Users/colethompson/Documents/A3/Updated/merged_index.csv'
SECONDARY_PATH = '/Users/colethompson/Documents/A3/Updated/secondary_index.csv'
MAPPING_PATH = '/Users/colethompson/Documents/A3/Updated/url_id_map.csv'

def load_mapping(mapping_path):
    mapping = {}
    with open(mapping_path, 'r') as file:
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
    docs = {}
    for token in query_tokens:
        postings_list = index_reader.get_postings_list(token)
        if postings_list is not None:
            for doc_id, doc_data in postings_list['doc_ids'].items():
                if doc_id not in docs:
                    docs[doc_id] = {}
                docs[doc_id][token] = doc_data['tf_idf']
    return docs

def compute_query_vector(query_tokens):
    query_vector = {}
    for token in query_tokens:
        if token not in query_vector:
            query_vector[token] = 0
        query_vector[token] += 1
    for token in query_vector:
        query_vector[token] = 1 + math.log10(query_vector[token])
    return query_vector

def calculate_cosine_similarity(doc_vector, query_vector):
    dot_product = sum(query_vector.get(token, 0) * weight for token, weight in doc_vector.items())
    doc_norm = math.sqrt(sum(weight ** 2 for weight in doc_vector.values()))
    query_norm = math.sqrt(sum(weight ** 2 for weight in query_vector.values()))
    
    if doc_norm == 0 or query_norm == 0:
        return 0.0

    return dot_product / (doc_norm * query_norm)


def top_k_documents(doc_vectors, query_vector, k):
    scores = []
    for doc_id, doc_vector in doc_vectors.items():
        score = calculate_cosine_similarity(doc_vector, query_vector)
        scores.append((score, doc_id))
    scores.sort(reverse=True)
    return scores[:k]

def search(query, index_reader, mapping, num_results=K_DOCUMENTS):
    start_time = time.time()

    query_tokens = preprocess_query(query)
    doc_vectors = get_docs(query_tokens, index_reader)
    query_vector = compute_query_vector(query_tokens)
    top_docs = top_k_documents(doc_vectors, query_vector, num_results)
    top_docs = [(mapping[doc_id], score) for score, doc_id in top_docs]

    print(f"Elapsed time: {(time.time() - start_time) * 1000} milliseconds")
    return top_docs

if __name__ == '__main__':
    index_reader = IndexReader(MERGED_PATH, SECONDARY_PATH)
    mapping = load_mapping(MAPPING_PATH)

    query = input("Search: ")
    print(search(query, index_reader, mapping))
