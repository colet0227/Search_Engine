import os
import json
from collections import defaultdict, Counter
import re

def parse_json_files(directory):
    docs = defaultdict(str)
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            if filename.endswith('.json'):
                with open(os.path.join(dirpath, filename), 'r') as f:
                    data = json.load(f)
                    docs[filename] = data['content']
    return docs

def tokenize(docs):
    pattern = r'[A-Za-z0-9]+'
    for doc_id, text in docs.items():
        words = re.findall(pattern, text)
        yield doc_id, Counter(words)

def build_index(tokens):
    index = defaultdict(list)
    for doc_id, token_counter in tokens:
        for token, frequency in token_counter.items():
            index[token].append((doc_id, frequency))
    return index

def main():
    docs = parse_json_files('/Users/colethompson/Documents/A3/ANALYST')
    tokens = tokenize(docs)
    index = build_index(tokens)

    with open('index.json', 'w') as f:
        json.dump(index, f)
    print(f'Size of index: {os.path.getsize("index.json") / 1024} KB')

    print(f'Number of documents: {len(docs)}')
    print(f'Number of unique tokens: {len(index)}')
    print(f'Size of index: {os.path.getsize("index.json") / 1024} KB')

if __name__ == '__main__':
    main()
