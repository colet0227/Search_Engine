import os
import json
from partial_indexer import PartialIndexer
from indexing import merge_partial_indices, generate_secondary_index, count_documents, calculate_tfidf

ROOT_DIR = '/Users/colethompson/Documents/A3/ANALYST'
SECONDARY_PATH = '/Users/colethompson/Documents/A3/Updated/secondary_index.csv'
MAPPING_PATH = '/Users/colethompson/Documents/A3/Updated/url_id_map.csv'
OUTPUT_PATH = '/Users/colethompson/Documents/A3/Updated'

if __name__ == "__main__":
    generate_secondary_index('/Users/colethompson/Documents/A3/Updated/merged_index.csv', SECONDARY_PATH)

    # partial_indexer = PartialIndexer()

    # root_dir = ROOT_DIR
    # file_paths = []

    # for dir_path, _, filenames in os.walk(root_dir):
    #     for file in filenames:
    #         if file.endswith(".json"):
    #             file_paths.append(os.path.join(dir_path, file))

    # url_id_map_path = MAPPING_PATH
    # merged_index_path = os.path.join(OUTPUT_PATH, 'merged_index.csv')

    # if os.path.exists(url_id_map_path):
    #     os.remove(url_id_map_path)

    # partial_index_paths = []
    # partial_index_count = 0

    # for path in file_paths:
    #     try:
    #         with open(path, 'r') as file:
    #             data = json.load(file)
    #             partial_indexer.add_document(data['content'], data['url'], url_id_map_path)
    #             print("Current index size: ", partial_indexer.current_size)  

    #             if partial_indexer.should_write_partial_index():
    #                 print(f'Writing partial index {partial_index_count}...')
    #                 partial_index_file = os.path.join(OUTPUT_PATH, f'partial_index_{partial_index_count}.csv')
    #                 partial_indexer.write_partial_index(partial_index_file)
    #                 partial_index_paths.append(partial_index_file)
    #                 partial_index_count += 1

    #     except Exception as e:
    #         print(f"Error processing file {path}: {e}")
    
    # if partial_indexer.current_size > 0:
    #     print(f'Writing final partial index {partial_index_count}...')
    #     partial_index_file = os.path.join(OUTPUT_PATH, f'partial_index_{partial_index_count}.csv')
    #     partial_indexer.write_partial_index(partial_index_file)
    #     partial_index_paths.append(partial_index_file)

    # merge_partial_indices(partial_index_paths, merged_index_path)
    # total_documents = count_documents(url_id_map_path)
    # calculate_tfidf(merged_index_path, total_documents)
    
    # for path in partial_index_paths:
    #     try:
    #         os.remove(path)
    #     except:
    #         pass
