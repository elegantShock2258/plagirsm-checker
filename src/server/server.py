import json
from urllib.parse import urlparse, parse_qs
from http.server import BaseHTTPRequestHandler, HTTPServer
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from nltk.stem import LancasterStemmer
import rabin_karp
import numpy as np
from os.path import dirname, join
import re


class PlagiarismChecker:
    def __init__(self, file_a, file_b):
        self.hash_table = {"a": [], "b": []}
        self.k_gram = 5

        self.calculate_hash(file_a, "a")
        self.calculate_hash(file_b, "b")

    def calculate_hash(self, content, doc_type):
        text = self.prepare_content(content)
        text = "".join(text)
        print(text)

        text = rabin_karp.rolling_hash(text, self.k_gram)
        for _ in range(len(content) - self.k_gram + 1):
            self.hash_table[doc_type].append(text.hash)
            if text.next_window() == False:
                break
        print(self.hash_table)

    def get_rate(self):
        return self.calaculate_plagiarism_rate(self.hash_table)

    def calaculate_plagiarism_rate(self, hash_table):
        th_a = len(hash_table["a"])
        th_b = len(hash_table["b"])
        a = hash_table["a"]
        b = hash_table["b"]
        sh = len(np.intersect1d(a, b))

        # Formular for plagiarism rate
        # P = (2 * SH / THA * THB ) 100%
        p = (float(2 * sh)/(th_a + th_b)) * 100
        val = [sh,a,b,th_a,th_b]
        return [val, p]

    # Prepare content by removing stopwords, steemming and tokenizing

    def prepare_content(self, content):
        # STOP WORDS
        stop_words = set(stopwords.words('english'))
        # TOKENIZE
        word_tokens = word_tokenize(content)

        filtered_content = []
        # STEMMING
        porter = PorterStemmer()
        for w in word_tokens:
            if w not in stop_words:
                w = w.lower()
                word = porter.stem(w)
                filtered_content.append(word)

        return filtered_content


def check_plagirism(a, b):
    checker = PlagiarismChecker(a, b)
    return checker.get_rate()


class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Parse the request URL
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)

        # Get the text1 and text2 parameters
        text1 = query_params.get('text1', [''])[0]
        text2 = query_params.get('text2', [''])[0]

        # Check if both parameters are provided
        if not text1 or not text2:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(
                bytes("Error: Both text1 and text2 parameters are required", "utf-8"))
            return

        # Run the plagiarism check function
        result = check_plagirism(text1, text2)  # Assuming check_plagiarism returns an array with elements "val" and "p"

        # Convert the result to JSON
        result_json = json.dumps({"val": result[0], "p": result[1]})

        # Send the response with the JSON data
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(bytes(result_json, "utf-8"))


def run_server(server_class=HTTPServer, handler_class=RequestHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Server started on port {port}")
    httpd.serve_forever()


if __name__ == '__main__':
    run_server()
