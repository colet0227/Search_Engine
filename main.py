import os
import json
import csv
import shutil
from partial_indexer import PartialIndexer


ROOT_DIR = '/Users/colethompson/Documents/A3/ANALYST'
SECONDARY_PATH = '/Users/colethompson/Documents/A3/Updated/secondary_index.csv'
MAPPING_PATH = '/Users/colethompson/Documents/A3/Updated/url_id_map.csv'
TEST_PATH = '/Users/colethompson/Documents/A3/Updated'


# This function merges multiple partial indices into a single index
def merge_partial_indices(partial_index_paths, merged_index_path):
    # Append the first partial index to the merged index
    with open(partial_index_paths[0], 'r') as f_in, open(merged_index_path, 'a') as f_out:
        # Skip header of first partial index
        next(f_in)

        # Copy the content of the first partial index into the merged index
        shutil.copyfileobj(f_in, f_out)

    # Delete the first partial index after copying
    os.remove(partial_index_paths[0])

    # For each remaining partial index, merge it with the current merged index
    for path in partial_index_paths[1:]:
        # Temporary merged index path
        temp_merged_index_path = merged_index_path + '.tmp'

        # Open partial as read only and use the created temporary path to write to
        with open(path, 'r') as partial_index_file, open(merged_index_path, 'r') as merged_index_file, open(temp_merged_index_path, 'w') as temp_merged_index_file:
            partial_index_reader = csv.DictReader(partial_index_file)
            merged_index_reader = csv.DictReader(merged_index_file)

            # Get field names from merged index file
            fieldnames = merged_index_reader.fieldnames

            # Create a dict writer to write to temporary csv file
            temp_merged_index_writer = csv.DictWriter(temp_merged_index_file, fieldnames=fieldnames)
            temp_merged_index_writer.writeheader()

            # Iterator until end and then return none
            # Represents rows in the partial and merged index csv files
            partial_row = next(partial_index_reader, None)
            merged_row = next(merged_index_reader, None)

            # Merge the current rows from the two indices
            while partial_row and merged_row:
                if partial_row['Token'] == merged_row['Token']:
                    merged_data = json.loads(merged_row['Data'])
                    token_data = json.loads(partial_row['Data'])

                    # Merge the data
                    merged_data['token_freq'] += token_data['token_freq']
                    merged_data['document_freq'] += token_data['document_freq']
                    merged_data['doc_ids'].update(token_data['doc_ids'])

                    # Write a new row to the temporary file
                    temp_merged_index_writer.writerow({'Token': merged_row['Token'], 'Data': json.dumps(merged_data)})
                    partial_row = next(partial_index_reader, None)
                    merged_row = next(merged_index_reader, None)

                elif partial_row['Token'] < merged_row['Token']:
                    temp_merged_index_writer.writerow(partial_row)
                    partial_row = next(partial_index_reader, None)
                else:
                    temp_merged_index_writer.writerow(merged_row)
                    merged_row = next(merged_index_reader, None)

            # Process the remaining rows of the longer file
            while partial_row:
                temp_merged_index_writer.writerow(partial_row)
                partial_row = next(partial_index_reader, None)
            
            while merged_row:
                temp_merged_index_writer.writerow(merged_row)
                merged_row = next(merged_index_reader, None)

        # Delete the old merged index and rename the temp to merged
        os.remove(merged_index_path)
        os.rename(temp_merged_index_path, merged_index_path)

        # Delete the processed partial index
        os.remove(path)


# This function generates a secondary index which maps each unique first letter of tokens to the file position where tokens with that first letter start
# Does this after merged index is already creaetd
def generate_secondary_index(merged_index_path, secondary_index_path):
    current_letter = ''

    # Open merged as read only and write to secondary index path
    with open(merged_index_path, 'r') as index_file, open(secondary_index_path, 'w', newline='') as secondary_index_file:
        secondary_index_writer = csv.writer(secondary_index_file)

        while True:
            # .tell() returns position to current cursor
            current_pos = index_file.tell()
            line = index_file.readline()

            # Break the loop if we've reached the end of the file
            if not line:
                break

            token = line.split(',')[0]  # Assuming token is the first column

            if token[0] != current_letter:
                current_letter = token[0]
                secondary_index_writer.writerow([current_letter, current_pos])

    return secondary_index_path


# Main function starts here
if __name__ == "__main__":
    partial_indexer = PartialIndexer()

    # Root directory path
    root_dir = ROOT_DIR
    file_paths = []

    # Walk through the directory tree and collect all JSON file paths
    for dir_path, _, filenames in os.walk(root_dir):
        for file in filenames:
            if file.endswith(".json"):
                file_paths.append(os.path.join(dir_path, file))

    secondary_index_path = SECONDARY_PATH
    url_id_map_path = MAPPING_PATH
    merged_index_path = os.path.join(TEST_PATH, 'merged_index.csv')

    # Create new merged index with header.
    with open(merged_index_path, 'w', newline='') as csvfile:
        fieldnames = ['Token', 'Data']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

    # Remove existing secondary index and url_id_map if they exist
    if os.path.exists(secondary_index_path):
        os.remove(secondary_index_path)
    if os.path.exists(url_id_map_path):
        os.remove(url_id_map_path)

    partial_index_paths = []
    partial_index_count = 0
    
    # For each JSON file, add its content to the partial index
    for path in file_paths:
        with open(path, 'r') as file:
            data = json.load(file)
            partial_indexer.add_document(data['content'], data['url'], url_id_map_path)

            print("Current index size: ", partial_indexer.current_size)  

            if partial_indexer.should_write_partial_index():
                print(f'Writing partial index {partial_index_count}...')
                partial_index_file = f'/Users/colethompson/Documents/A3/Updated/partial_index_{partial_index_count}.csv'
                partial_indexer.write_partial_index(partial_index_file)
                partial_index_paths.append(partial_index_file)
                partial_index_count += 1

    # After all JSON files are processed, merge the partial indices into a single index and generate a secondary index
    merge_partial_indices(partial_index_paths, merged_index_path)
    generate_secondary_index(merged_index_path, secondary_index_path)
