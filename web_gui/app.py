import sys
sys.path.insert(0, '../')

from flask import Flask, render_template, request
from retrieval import search as search_func, IndexReader, load_mapping

# Instantiate a Flask web application
app = Flask(__name__)

# File paths to the necessary indexes and mappings
MERGED_PATH = '/Users/colethompson/Documents/A3/Updated/merged_index.csv'
SECONDARY_PATH = '/Users/colethompson/Documents/A3/Updated/secondary_index.csv'
MAPPING_PATH = '/Users/colethompson/Documents/A3/Updated/url_id_map.csv'

# Instantiate an IndexReader and load the mapping
index_reader = IndexReader(MERGED_PATH, SECONDARY_PATH)
mapping = load_mapping(MAPPING_PATH)

# Define the search function, performing a paginated search
def search(query, page=1, per_page=10):
    # Get all search results for the query
    all_results = search_func(query, index_reader, mapping, 100) # 10 pages worth of results

    # Calculate the starting index of the results for the current page
    start = (page - 1) * per_page

    # Calculate the ending index of the results for the current page
    end = start + per_page

    # Return only the results for the current page
    return all_results[start:end]

# Define the route for the search page
@app.route('/search', methods=['GET', 'POST'])
def search_page():
    results = []

    # Get the query, page, and per_page parameters from the GET request
    query = request.args.get('query', '', type=str)
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    if request.method == 'POST':
        query = request.form['query']
        results = search(query, page, per_page)
    elif query:
        results = search(query, page, per_page)

    print(f'Returning results for page {page}: {results}')  # Debug print

    # Render the search page with the current results, query, and pagination parameters
    return render_template('search.html', results=results, query=query, page=page, per_page=per_page)


@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(port=5001)
