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
import base64
import json
import threading
import math as Math


class PlagiarismChecker:
    def __init__(self, file_a, file_b):
        stop_words = set(stopwords.words('english'))

        self.hash_table = {"a": [], "b": []}
        self.k_gram = 400 + Math.ceil(max(len(file_a), len(file_b))*0.0001 + 1)

        thread1 = threading.Thread(
            target=self.calculate_hash, args=(file_a, "a", stop_words))
        thread2 = threading.Thread(
            target=self.calculate_hash, args=(file_b, "b", stop_words))

        thread1.start()
        thread2.start()

        thread1.join()
        thread2.join()

    def calculate_hash(self, content, doc_type, stop_words):
        text = self.prepare_content(content, stop_words)
        text = "".join(text)
        text = rabin_karp.rolling_hash(text, self.k_gram)
        for _ in range(len(content) - self.k_gram + 1):
            self.hash_table[doc_type].append(text.hash)
            if text.next_window() == False:
                break

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
        val = [sh, th_a, th_b]
        return [val, p]

    # Prepare content by removing stopwords, steemming and tokenizing

    def prepare_content(self, content, stop_words):
        # STOP WORDS
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
    def end_headers (self):
        self.send_header('Access-Control-Allow-Origin', '*')
        BaseHTTPRequestHandler.end_headers(self)

    def do_POST(self):

        # Get content length from headers
        content_length = int(self.headers['Content-Length'])
        # Read the request body
        post_data = json.loads(self.rfile.read(content_length).decode('utf-8'))
        d1 = (post_data['d1'])
        d2 = (post_data['d2'])
        
        if 'd1' in post_data and 'd2' in post_data:
            print("got d1 and d2", len(d1), len(d2))
            result = check_plagirism(d1, d2)
            print(result)
            result_json = json.dumps({"val": result[0], "p": result[1]}).encode()

            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(result_json)
        else:
            self.send_response(400)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Missing d1 and d2"}).encode())


def run_server(server_class=HTTPServer, handler_class=RequestHandler, port=4437):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Server started on port {port}")
    httpd.serve_forever()


if __name__ == '__main__':
    run_server()
