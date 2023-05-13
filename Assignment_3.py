import os
import json
from collections import defaultdict, Counter
import re
from typing import Dict, Tuple, List

def parse_json_files(directory: str) -> Dict[str, str]:
    """
    Parse JSON files in a given directory and return a dictionary
    with the content of each file as a value and filename as a key.

    Args:
        directory: A string containing the path to the directory.

    Returns:
        A dictionary with the content of each file as a value and filename as a key.
    """
    docs = defaultdict(str)
    for dirpath, dirnames, filenames in os.walk(directory):
        for filename in filenames:
            if filename.endswith('.json'):
                with open(os.path.join(dirpath, filename), 'r') as f:
                    data = json.load(f)
                    docs[filename] = data['content']
    return docs

def tokenize(docs: Dict[str, str]) -> List[Tuple[str, Counter]]:
    """
    Tokenize text from a dictionary of documents using regular expressions
    and return a list of tuples containing the document ID and a Counter object
    with the frequency of each token in the document.

    Args:
        docs: A dictionary with the content of each document as a value and document ID as a key.

    Returns:
        A list of tuples with the document ID and a Counter object with the frequency of each token in the document.
    """
    for doc_id, text in docs.items():
        words = re.sub('[^0-9a-zA-Z]+', ' ', text).lower().split()
        yield doc_id, Counter(words)

def build_index(tokens: List[Tuple[str, Counter]]) -> Dict[str, List[Tuple[str, int]]]:
    """
    Build an inverted index from a list of tokens using a dictionary of lists.

    Args:
        tokens: A list of tuples with the document ID and a Counter object with the frequency of each token in the document.

    Returns:
        A dictionary of lists with the token as a key and a list of tuples containing the document ID and frequency of the token in the document.
    """
    index = defaultdict(list)
    for doc_id, token_counter in tokens:
        for token, frequency in token_counter.items():
            index[token].append((doc_id, frequency))
    return index

def main() -> None:
    """
    Main function that parses JSON files, tokenizes them, builds an inverted index,
    and saves the index to a JSON file.
    """
    docs = parse_json_files('/Users/simarcheema/Desktop/Search_Engine/ANALYST')
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