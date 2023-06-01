import json
import math
import os
import csv
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
    with open(merged_index_path, 'r') as merged_index, open(secondary_index_path, 'w', newline='') as secondary_index:
        writer = csv.writer(secondary_index)

        line = merged_index.readline()
        while line:
            byte_offset = merged_index.tell() - len(line) - 1  # "-1" accounts for newline character
            token = line.split(",")[0]
            writer.writerow([token, byte_offset])
            line = merged_index.readline()

def calculate_tfidf(merged_index_path, total_documents):
    temp_merged_index_path = merged_index_path + '.tmp'
    with open(merged_index_path, 'r') as infile, open(temp_merged_index_path, 'w') as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)
        for row in reader:
            if row:  # Check that row is not empty
                token = row[0]
                data_str = row[1]
                try:
                    data = json.loads(data_str)
                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON data for line: {row}")
                    continue

                idf = math.log(total_documents / data['document_freq'])

                for doc_id, doc_info in data['doc_ids'].items():
                    tf = 1 + math.log(doc_info['freq'])
                    tf_idf = tf * idf

                    doc_info['tf_idf'] = tf_idf * doc_info['weight']

                writer.writerow([token, json.dumps(data)])

    os.remove(merged_index_path)
    os.rename(temp_merged_index_path, merged_index_path)
