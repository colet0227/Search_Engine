import os
import json
import nltk
from collections import defaultdict, Counter
from nltk.corpus import stopwords

# Download the NLTK stop words
nltk.download('punkt')
nltk.download('stopwords')