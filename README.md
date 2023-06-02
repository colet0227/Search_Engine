# Search Engine
<img width="1440" alt="Screenshot 2023-06-02 at 10 10 29 AM" src="https://github.com/colet0227/Search_Engine/assets/10394057/62c09412-679b-4607-b47b-f6a968d9f59c">
<img width="1440" alt="Screenshot 2023-06-02 at 10 10 36 AM" src="https://github.com/colet0227/Search_Engine/assets/10394057/b605f62e-9a6f-49dd-a981-9679edef68ea">
<img width="1440" alt="Screenshot 2023-06-02 at 10 10 42 AM" src="https://github.com/colet0227/Search_Engine/assets/10394057/315babed-0c8c-4f48-87c2-c26dd4130859">


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
