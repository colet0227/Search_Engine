# Assignment 3

from bs4 import BeautifulSoup
import os

html_dir = ""

text_dict = {}

for file_name in os.listdir(html_dir):
    if file_name.endswith(".html"):
        file_path = os.path.join(html_dir, file_name)
        with open(file_path, "r", encoding="utf-8") as f:
            # parse HTML with Beautiful Soup
            soup = BeautifulSoup(f, "html.parser")
            # extract text content from HTML
            text = soup.get_text()
            # store text content in dictionary
            text_dict[file_name] = text