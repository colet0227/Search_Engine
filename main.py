# import os
# import json
# from partial_indexer import PartialIndexer
# from indexing import merge_partial_indices, generate_secondary_index, count_documents, calculate_tfidf

# # ROOT_DIR = '/Users/colethompson/Documents/A3/ANALYST'
# ROOT_DIR = '/Users/colethompson/Documents/A3/DEV'
# SECONDARY_PATH = '/Users/colethompson/Documents/A3/Updated/secondary_index.txt'
# MAPPING_PATH = '/Users/colethompson/Documents/A3/Updated/url_id_map.txt'
# OUTPUT_PATH = '/Users/colethompson/Documents/A3/Updated'

# if __name__ == "__main__":
#     # generate_secondary_index('/Users/colethompson/Documents/A3/Updated/merged_index.txt', SECONDARY_PATH)




#     partial_indexer = PartialIndexer()

#     # Root directory path
#     root_dir = ROOT_DIR
#     file_paths = []

#     # Walk through the directory tree and collect all JSON file paths
#     for dir_path, _, filenames in os.walk(root_dir):
#         for file in filenames:
#             if file.endswith(".json"):
#                 file_paths.append(os.path.join(dir_path, file))

#     secondary_index_path = SECONDARY_PATH
#     url_id_map_path = MAPPING_PATH
#     merged_index_path = os.path.join(OUTPUT_PATH, 'merged_index.txt')

#     # Remove existing secondary index and url_id_map if they exist
#     if os.path.exists(secondary_index_path):
#         os.remove(secondary_index_path)
#     if os.path.exists(url_id_map_path):
#         os.remove(url_id_map_path)

#     partial_index_paths = []
#     partial_index_count = 0

#     # For each JSON file, add its content to the partial index
#     for path in file_paths:
#         try:
#             with open(path, 'r') as file:
#                 data = json.load(file)
#                 partial_indexer.add_document(data['content'], data['url'], url_id_map_path)
#                 print("Current index size: ", partial_indexer.current_size)  

#                 if partial_indexer.should_write_partial_index():
#                     print(f'Writing partial index {partial_index_count}...')
#                     partial_index_file = os.path.join(OUTPUT_PATH, f'partial_index_{partial_index_count}.txt')
#                     partial_indexer.write_partial_index(partial_index_file)
#                     partial_index_paths.append(partial_index_file)
#                     partial_index_count += 1

#         except Exception as e:
#             print(f"Error processing file {path}: {e}")
    
#     # Write the remaining entries in the indexer to a partial index.
#     if partial_indexer.current_size > 0:
#         print(f'Writing final partial index {partial_index_count}...')
#         partial_index_file = os.path.join(OUTPUT_PATH, f'partial_index_{partial_index_count}.txt')
#         partial_indexer.write_partial_index(partial_index_file)
#         partial_index_paths.append(partial_index_file)

#     # After all JSON files are processed, merge the partial indices into a single index and generate a secondary index
#     merge_partial_indices(partial_index_paths, merged_index_path)
#     # wait 10 seconds
#     generate_secondary_index('/Users/colethompson/Documents/A3/Updated/merged_index.txt', secondary_index_path)
#     total_documents = count_documents(url_id_map_path)
#     calculate_tfidf(merged_index_path, total_documents)
    
#     # Clean up
#     for path in partial_index_paths:
#         try:
#             os.remove(path)
#         except:
#             pass






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

    # secondary_index_path = SECONDARY_PATH
    # url_id_map_path = MAPPING_PATH
    # merged_index_path = os.path.join(OUTPUT_PATH, 'merged_index.csv')

    # if os.path.exists(secondary_index_path):
    #     os.remove(secondary_index_path)
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
    # # generate_secondary_index('/Users/colethompson/Documents/A3/Updated/merged_index.csv', secondary_index_path)
    # total_documents = count_documents(url_id_map_path)
    # calculate_tfidf(merged_index_path, total_documents)
    
    # for path in partial_index_paths:
    #     try:
    #         os.remove(path)
    #     except:
    #         pass
