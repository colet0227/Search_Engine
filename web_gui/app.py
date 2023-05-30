import sys
sys.path.append("..")

from flask import Flask, render_template, request
from retrieval import search, IndexReader, load_mapping

app = Flask(__name__)

MERGED_PATH = '/Users/colethompson/Documents/A3/Updated/merged_index.txt'
SECONDARY_PATH = '/Users/colethompson/Documents/A3/Updated/secondary_index.txt'
MAPPING_PATH = '/Users/colethompson/Documents/A3/Updated/url_id_map.txt'

index_reader = IndexReader(MERGED_PATH, SECONDARY_PATH)
mapping = load_mapping(MAPPING_PATH)

@app.route('/search', methods=['GET', 'POST'])
def search_page():
    if request.method == 'POST':
        query = request.form['query']
        results = search(query, index_reader, mapping)
        return render_template('search.html', results=results)
    return render_template('search.html')

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
