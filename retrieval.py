import re
import csv
import json
import sys
from nltk.stem import SnowballStemmer

stemmer = SnowballStemmer("english")
MERGED_PATH = '/Users/colethompson/Documents/A3/Updated/merged_index.csv'
SECONDARY_PATH = '/Users/colethompson/Documents/A3/Updated/secondary_index.csv'
MAPPING_PATH = '/Users/colethompson/Documents/A3/Updated/url_id_map.csv'

def load_secondary_index(secondary_index_path):
    secondary_index = {}
    with open(secondary_index_path, 'r') as f:
        reader = csv.reader(f)
        for row in reader:
            secondary_index[row[0]] = int(row[1])
    return secondary_index

def preprocess_query(query):
    query = query.lower()
    query = re.sub(r'\W+', ' ', query)
    query_tokens = query.split()
    query_tokens = [stemmer.stem(token) for token in query_tokens]
    return query_tokens

def get_postings_list(token, secondary_index, index_file):
    first_char = token[0]
    if first_char in secondary_index:
        position = secondary_index[first_char]
        index_file.seek(position)
        csv.field_size_limit(sys.maxsize)
        reader = csv.reader(index_file)
        for row in reader:
            row_token, row_data = row[0], row[1]
            if row_token == token:
                return json.loads(row_data)
    return None


def get_docs(query_tokens, secondary_index, index_file):
    doc_lists = []
    for token in query_tokens:
        postings_list = get_postings_list(token, secondary_index, index_file)
        if postings_list is not None:
            docs = postings_list.get('doc_ids', {}).keys()
            doc_lists.append(set(docs))
    return doc_lists

def intersect_doc_lists(doc_lists):
    if not doc_lists:
        return set()
    intersected_list = doc_lists[0]
    for doc_list in doc_lists[1:]:
        intersected_list = intersected_list.intersection(doc_list)
    return intersected_list

def calculate_scores(intersected_list, query_tokens, secondary_index, index_file):
    scores = {}
    for doc_id in intersected_list:
        scores[doc_id] = 0
        for token in query_tokens:
            postings_list = get_postings_list(token, secondary_index, index_file)
            if postings_list is not None:
                doc_data = postings_list['doc_ids'].get(doc_id)
                if doc_data:
                    tf_idf = doc_data['tf_idf']
                    weight = doc_data['weight']
                    score = weight + tf_idf
                    scores[doc_id] += score
    return scores

def rank_documents(scores):
    ranked_docs = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return ranked_docs[:5]

def load_mapping(mapping_path):
    with open(mapping_path, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip the header row if there is one
        mapping = {rows[0]: rows[1] for rows in reader}
    return mapping

def search(query, index_file, secondary_index, mapping):
    query_tokens = preprocess_query(query)
    print(f"Preprocessed query tokens: {query_tokens}")

    doc_lists = get_docs(query_tokens, secondary_index, index_file)
    print(f"Doc lists: {doc_lists}")

    intersected_docs = intersect_doc_lists(doc_lists)
    print(f"Intersected Docs: {intersected_docs}")

    scores = calculate_scores(intersected_docs, query_tokens, secondary_index, index_file)
    print(f"Scores: {scores}")

    top_docs = rank_documents(scores)
    print(f"Top Docs before mapping: {top_docs}")

    top_docs = [(mapping[doc_id], score) for doc_id, score in top_docs]
    print(f"Top Docs after mapping: {top_docs}")

    return top_docs


if __name__ == '__main__':
    secondary_index_path = SECONDARY_PATH
    merged_index_path = MERGED_PATH
    mapping_path = MAPPING_PATH

    secondary_index = load_secondary_index(secondary_index_path)
    mapping = load_mapping(mapping_path)

    query = input("Search: ")
    
    with open(merged_index_path, 'r') as index_file:
        top_docs = search(query, index_file, secondary_index, mapping)
    print(top_docs)
