import json
import math
import os
import shutil

def count_documents(url_id_map_path):
    with open(url_id_map_path, 'r') as file:
        return sum(1 for _ in file)  # Count number of lines

def merge_partial_indices(partial_index_paths, merged_index_path):
    with open(partial_index_paths[0], 'r') as f_in, open(merged_index_path, 'w') as f_out:
        # Copy the content of the first partial index into the merged index
        shutil.copyfileobj(f_in, f_out)
    os.remove(partial_index_paths[0])  # Delete the first partial index after copying

    # For each remaining partial index, merge it with the current merged index
    for path in partial_index_paths[1:]:
        temp_merged_index_path = merged_index_path + '.tmp'  # Temporary merged index path

        with open(path, 'r') as partial_index_file, open(merged_index_path, 'r') as merged_index_file, open(temp_merged_index_path, 'w') as temp_merged_index_file:
            partial_line = next(partial_index_file, None)
            merged_line = next(merged_index_file, None)

            while partial_line and merged_line:
                # Skip lines in partial index that don't contain a ":"
                if ":" not in partial_line:
                    partial_line = next(partial_index_file, None)
                    continue

                # Skip lines in merged index that don't contain a ":"
                if ":" not in merged_line:
                    merged_line = next(merged_index_file, None)
                    continue

                partial_token, partial_data = partial_line.strip().split(":", 1)  # Add 1 to split only once
                merged_token, merged_data = merged_line.strip().split(":", 1)  # Add 1 to split only once

                partial_data = json.loads(partial_data)
                merged_data = json.loads(merged_data)

                if partial_token == merged_token:
                    merged_data['token_freq'] += partial_data['token_freq']
                    merged_data['document_freq'] += partial_data['document_freq']
                    merged_data['doc_ids'].update(partial_data['doc_ids'])

                    temp_merged_index_file.write(f'{merged_token}: {json.dumps(merged_data)}\n')

                    partial_line = next(partial_index_file, None)
                    merged_line = next(merged_index_file, None)
                elif partial_token < merged_token:
                    temp_merged_index_file.write(partial_line)
                    partial_line = next(partial_index_file, None)
                else:
                    temp_merged_index_file.write(merged_line)
                    merged_line = next(merged_index_file, None)

            # Process the remaining lines of the longer file
            while partial_line:
                temp_merged_index_file.write(partial_line)
                partial_line = next(partial_index_file, None)

            while merged_line:
                temp_merged_index_file.write(merged_line)
                merged_line = next(merged_index_file, None)

        os.remove(merged_index_path)  # Delete the old merged index
        os.rename(temp_merged_index_path, merged_index_path)  # Rename the temp to merged

        os.remove(path)  # Delete the processed partial index



def generate_secondary_index(merged_index_path, secondary_index_path):
    with open(merged_index_path, 'r') as merged_index, open(secondary_index_path, 'w') as secondary_index:
        # last_token = None
        j = 0

        while True:
            i = j

            line = merged_index.readline()
            # print(line)
            # break
            if not line:
                break
            
            for _ in line:
                j += 1

            token, json_data = line.split(':', 1)  # split only once, so that the token can contain ":"

            secondary_index.write(f'{token}:{i}\n')

def calculate_tfidf(merged_index_path, total_documents):
    with open(merged_index_path, 'r') as merged_index, open(merged_index_path + '.tmp', 'w') as new_merged_index:
        for line in merged_index:
            token, data_str = line.strip().split(':', 1)
            try:
                data = json.loads(data_str)

                idf = math.log(total_documents / data['document_freq'])

                for doc_id, doc_info in data['doc_ids'].items():
                    tf = 1 + math.log(doc_info['freq'])
                    tf_idf = tf * idf

                    doc_info['tf_idf'] = tf_idf * doc_info['weight']

                new_merged_index.write(f'{token}:{json.dumps(data)}\n')

            except json.JSONDecodeError:
                print(f"Error parsing JSON data for line: {line}")
                continue

    os.remove(merged_index_path)
    os.rename(merged_index_path + '.tmp', merged_index_path)
