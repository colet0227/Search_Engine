# Search Engine
<img width="1440" alt="Screenshot 2023-06-02 at 10 05 12 AM" src="https://github.com/colet0227/Search_Engine/assets/10394057/e0ba9ca6-664f-4264-9dee-39f94321663a">
<img width="1440" alt="Screenshot 2023-06-02 at 10 06 12 AM" src="https://github.com/colet0227/Search_Engine/assets/10394057/25836bf8-2c5a-4da8-bcb3-710903afa0e7">
<img width="1440" alt="Screenshot 2023-06-02 at 10 06 32 AM" src="https://github.com/colet0227/Search_Engine/assets/10394057/c03214e9-4f37-4b10-8be6-f2c7d1d48d16">

# How to Run:

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
