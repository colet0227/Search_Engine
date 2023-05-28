import shutil
import math
import csv
import os
import json

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

def count_documents(url_id_map_path):
    with open(url_id_map_path, 'r') as file:
        return sum(1 for row in csv.reader(file)) - 1  # Subtract 1 to account for header row

def calculate_tfidf(merged_index_path, total_documents):
    temp_merged_index_path = merged_index_path + '.tmp'
    
    with open(merged_index_path, 'r') as merged_index_file, open(temp_merged_index_path, 'w') as temp_merged_index_file:
        merged_index_reader = csv.DictReader(merged_index_file)
        fieldnames = merged_index_reader.fieldnames
        temp_merged_index_writer = csv.DictWriter(temp_merged_index_file, fieldnames=fieldnames)
        temp_merged_index_writer.writeheader()

        for row in merged_index_reader:
            token_data = json.loads(row['Data'])

            idf = math.log(total_documents / token_data['document_freq'])
            for doc_id, doc_info in token_data['doc_ids'].items():
                tf = doc_info['freq']  # changed to get the term frequency for this specific document
                tf_idf = (1 + math.log(tf)) * idf
                doc_info['tf_idf'] = tf_idf

            temp_merged_index_writer.writerow({'Token': row['Token'], 'Data': json.dumps(token_data)})

    os.remove(merged_index_path)
    os.rename(temp_merged_index_path, merged_index_path) 


