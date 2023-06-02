How to run Search Engine:

Prerequisites:
    - macOS 10.15+
    - Python 3.9+

Setup:
    - Ensure necessary Python packages are installed
        - pip install flask
        - pip install nltk
        - pip install beautifulsoup4
            - Depending on system, you may need to use "pip3" instead of "pip"

Indexing:
    - Replace root files in "retrieval.py" and "main.py" to match your system
    - First run main.py without generating secondary index
        - This is because there is a byte offset error when we try doing it immediately after
        - python3 main.py
    - The merged index should be finished between 1-2 hours if using DEV directory
    - After this is complete comment out other code in __main__ function and generate secondary index
        - python3 main.py
    - You should now have a "merged_index.csv", "secondary_index.csv", and "url_id_map.csv" file

Terminal GUI:
    - python3 retrieval.py

Web GUI:
    - Enter web gui directory
        - cd web_gui/
    - python3 app.py
    - You can view development server at "http://127.0.0.1:5001"