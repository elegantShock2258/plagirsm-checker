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
import cgi

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
        val = [sh, a, b, th_a, th_b]
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
    def do_POST(self):
  
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length).decode('utf-8')
        if self.headers.get('Content-Type', "") == "application/x-www-form-urlencoded":
        
            d1 = query_params['d1'][0]
            d2 = query_params['d2'][0]
            print(d1, d2)
            result = check_plagirism(d1, d2)

            result_json = json.dumps({"val": result[0], "p": result[1]})

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(bytes(result_json, "utf-8"))
        else:
            self.send_response(400)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(
                bytes('Bad Request: Missing form data parameters', 'utf-8'))


def run_server(server_class=HTTPServer, handler_class=RequestHandler, port=4437):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Server started on port {port}")
    httpd.serve_forever()


if __name__ == '__main__':
    run_server()
