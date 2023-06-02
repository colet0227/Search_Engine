import sys
from flask import Flask, render_template, request
from retrieval import search as search_func, IndexReader, load_mapping

app = Flask(__name__)

MERGED_PATH = '/Users/colethompson/Documents/A3/Updated/merged_index.csv'
SECONDARY_PATH = '/Users/colethompson/Documents/A3/Updated/secondary_index.csv'
MAPPING_PATH = '/Users/colethompson/Documents/A3/Updated/url_id_map.csv'

index_reader = IndexReader(MERGED_PATH, SECONDARY_PATH)
mapping = load_mapping(MAPPING_PATH)

def search(query, page=1, per_page=10):
    all_results = search_func(query, index_reader, mapping)
    start = (page - 1) * per_page
    end = start + per_page
    return all_results[start:end]

@app.route('/search', methods=['GET', 'POST'])
def search_page():
    results = []
    query = request.args.get('query', '', type=str)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    if request.method == 'POST':
        query = request.form['query']
        results = search(query, page, per_page)
    elif query:
        results = search(query, page, per_page)

    return render_template('search.html', results=results, query=query, page=page, per_page=per_page)

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(port=5001)
