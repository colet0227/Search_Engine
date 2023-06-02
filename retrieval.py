import csv
import json
import time
import re
import math
from collections import defaultdict
from nltk.stem import SnowballStemmer

# Return how many documents
K_DOCUMENTS = 10

class IndexReader:
    # Class to load in secondary index and get postings
    def __init__(self, merged_index_path, secondary_index_path):
        self.secondary_index = self.load_secondary_index(secondary_index_path)
        self.index_file = open(merged_index_path, 'r')

    # Load the secondary index file
    def load_secondary_index(self, secondary_index_path):
        secondary_index = {}
        with open(secondary_index_path, 'r') as f:
            reader = csv.reader(f)
            for token, offset in reader:
                secondary_index[token] = int(offset)
        return secondary_index

    # Get postings list for a token
    def get_postings_list(self, token):
        # Using get instead of the [] operator will return none if the token isn't there
        line_start = self.secondary_index.get(token)

        if line_start:
            # Jump to byte offset
            self.index_file.seek(line_start)

            # Split the line in file by comma and then get dictionary
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
    # Load in the mapping to memory
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
    # Tokenize query
    words = re.findall(r'[a-zA-Z0-9]+', query)
    return [stemmer.stem(token.lower()) for token in words]

def get_docs(query_tokens, index_reader):
    # Get documents for query tokens
    docs = {}
    for token in query_tokens:
        # Get postings for each token
        postings_list = index_reader.get_postings_list(token)

        if postings_list:
            for doc_id, doc_data in postings_list['doc_ids'].items():
                # Add the document id to docs
                if doc_id not in docs:
                    docs[doc_id] = {}
                
                # Maps tokens to their tf-idf scores in the corresponding document
                # Compute the cosine similarity
                docs[doc_id][token] = doc_data['tf_idf']
    return docs

def compute_query_vector(query_tokens):
    query_vector = defaultdict(int)

    # Increment the count for this token
    for token in query_tokens:
        query_vector[token] += 1  

    # Update the count for this token to its log frequency
    for token in query_vector:
        # Calculate term frequency for user query
        query_vector[token] = 1 + math.log10(query_vector[token])  
    
    return query_vector

def calculate_cosine_similarity(doc_vector, query_vector):
    # Calculate the dot product of the document vector and the query vector
    dot_product = sum(query_vector.get(token, 0) * weight for token, weight in doc_vector.items())

    # Calculate the magnitude (Euclidean norm) of the document vector
    doc_norm = math.sqrt(sum(weight ** 2 for weight in doc_vector.values()))

    # Calculate the magnitude (Euclidean norm) of the query vector
    query_norm = math.sqrt(sum(weight ** 2 for weight in query_vector.values()))
    
    # If either vector has zero magnitude their cosine similarity is undefined
    if doc_norm == 0 or query_norm == 0:
        return 0.0

    # Return cosine similarity (dot product divided by the product of their magnitudes)
    return dot_product / (doc_norm * query_norm)


def top_k_documents(doc_vectors, query_vector, k):
    # Initialize an empty list to hold the cosine similarity scores
    scores = []

    # Calculate the cosine similarity between this document vector and the query vector
    for doc_id, doc_vector in doc_vectors.items():
        score = calculate_cosine_similarity(doc_vector, query_vector)
        scores.append((score, doc_id))
    
    # Return the top-k scores (K_DOCUMENTS)
    scores.sort(reverse=True)
    return scores[:k]

def search(query, index_reader, mapping, num_results=K_DOCUMENTS):
    # Record the start time of the search
    start_time = time.time()

    query_tokens = preprocess_query(query)
    doc_vectors = get_docs(query_tokens, index_reader)
    query_vector = compute_query_vector(query_tokens)
    top_docs = top_k_documents(doc_vectors, query_vector, num_results)

    # Return the url and its score for the top k documents
    top_docs = [(mapping[doc_id], score) for score, doc_id in top_docs]

    # Print total query dispatch time
    print(f"Elapsed time: {(time.time() - start_time) * 1000} milliseconds")
    return top_docs

if __name__ == '__main__':
    index_reader = IndexReader(MERGED_PATH, SECONDARY_PATH)
    mapping = load_mapping(MAPPING_PATH)

    query = input("Search: ")
    print(search(query, index_reader, mapping))
