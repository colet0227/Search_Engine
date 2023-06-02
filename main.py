import os
import json
import csv
import sys
from partial_indexer import PartialIndexer
from indexing import merge_partial_indices, generate_secondary_index, count_documents, calculate_tfidf

# CHANGE PATHS FOR YOUR OWN COMPUTER
ROOT_DIR = '/Users/colethompson/Documents/A3/DEV'
SECONDARY_PATH = '/Users/colethompson/Documents/A3/Updated/secondary_index.csv'
MAPPING_PATH = '/Users/colethompson/Documents/A3/Updated/url_id_map.csv'
OUTPUT_PATH = '/Users/colethompson/Documents/A3/Updated'

if __name__ == "__main__":
    ###########
    ###########
    ###########
    ###########
    # FIRST DO MAIN LOOP AND THEN UNCOMMENT AND GENERATE SECONDARY INDEX AFTER. OTHERWISE, THERES AND ERROR WITH BYTE OFFSET
    # generate_secondary_index('/Users/colethompson/Documents/A3/Updated/merged_index.csv', SECONDARY_PATH)
    ###########
    ###########
    ###########
    ###########

    # Otherwise field larger than field limit (131072)
    csv.field_size_limit(sys.maxsize)

    # Initialize a new partial indexer
    partial_indexer = PartialIndexer()

    root_dir = ROOT_DIR
    file_paths = []

    # Collect all json file paths (documents)
    for dir_path, _, filenames in os.walk(root_dir):
        for file in filenames:
            if file.endswith(".json"):
                file_paths.append(os.path.join(dir_path, file))

    url_id_map_path = MAPPING_PATH
    merged_index_path = os.path.join(OUTPUT_PATH, 'merged_index.csv')

    # Delete existing url_id_map if it exists
    if os.path.exists(url_id_map_path):
        os.remove(url_id_map_path)

    partial_index_paths = []
    partial_index_count = 0

    # Index each json file
    for path in file_paths:
        try:
            with open(path, 'r') as file:
                data = json.load(file)

                # Add document content to the partial index
                partial_indexer.add_document(data['content'], data['url'], url_id_map_path)

                # Print for debugging purposes
                print("Current index size: ", partial_indexer.current_size)  

                # Write partial index to disk if it is large enough
                if partial_indexer.should_write_partial_index():
                    print(f'Writing partial index {partial_index_count}...')
                    partial_index_file = os.path.join(OUTPUT_PATH, f'partial_index_{partial_index_count}.csv')
                    partial_indexer.write_partial_index(partial_index_file)
                    partial_index_paths.append(partial_index_file)
                    partial_index_count += 1

        except Exception as e:
            print(f"Error processing file {path}: {e}")
    
    # If there is remaining data in the partial index, write it to disk
    if partial_indexer.current_size > 0:
        print(f'Writing final partial index {partial_index_count}...')
        partial_index_file = os.path.join(OUTPUT_PATH, f'partial_index_{partial_index_count}.csv')
        partial_indexer.write_partial_index(partial_index_file)
        partial_index_paths.append(partial_index_file)

    # Merge all partial indices into a single index
    merge_partial_indices(partial_index_paths, merged_index_path)

    # Count total number of documents
    total_documents = count_documents(url_id_map_path)

    # Calculate tf-idf for each term in each document
    calculate_tfidf(merged_index_path, total_documents)
    
    # Clean up partial index files
    for path in partial_index_paths:
        try:
            os.remove(path)
        except:
            pass
