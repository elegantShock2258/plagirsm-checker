#include <bitset>
#include <cmath>
#include <crow.h>
#include <crow/http_request.h>
#include <iostream>
#include <nlohmann/json.hpp>
#include <string>
#include <vector>

class BloomFilter {
  std::bitset<1000> bitset;
  int numHashes;

public:
  BloomFilter(int numHashes) : numHashes(numHashes) {}

  unsigned int hash1(std::string &input) {
    unsigned int value = 0;
    for (char c : input) {
      value = value * 101 + c;
    }
    return value;
  }

  unsigned int hash2(std::string &input) {
    unsigned int value = 0;
    for (char c : input) {
      value = value * 103 + c;
    }
    return value;
  }

  void add(std::string &input) {
    for (int n = 0; n < numHashes; n++) {
      unsigned int hashValue =
          (hash1(input) + n * hash2(input)) % bitset.size();
      bitset[hashValue] = 1;
    }
  }

  bool possiblyContains(std::string &input) {
    for (int n = 0; n < numHashes; n++) {
      unsigned int hashValue =
          (hash1(input) + n * hash2(input)) % bitset.size();
      if (bitset[hashValue] == 0) {
        return false;
      }
    }
    return true;
  }
};

class RollingHash {
public:
  std::string text;
  int patternSize;
  int base = 26;
  int window_start = 0;
  int window_end = 0;
  int mod = 11932;
  int hash;

  RollingHash(std::string text, int patternSize) {
    this->text = text;
    this->patternSize = patternSize;
    this->hash = get_hash(text, patternSize);
  }

  int get_hash(std::string text, int patternSize) {
    int hash_value = 0;
    for (int i = 0; i < patternSize; i++) {
      hash_value =
          ((long long)(hash_value +
                       (text[i] - 96) * pow(base, patternSize - i - 1))) %
          this->mod;
    }
    this->window_start = 0;
    this->window_end = patternSize;
    return hash_value;
  }

  bool next_window() {
    if (this->window_end <= text.length() - 1) {
      this->hash -=
          (text[this->window_start] - 96) * pow(base, this->patternSize - 1);
      this->hash *= base;
      this->hash += text[this->window_end] - 96;
      this->hash %= mod;
      this->window_start += 1;
      this->window_end += 1;
      return true;
    }
    return false;
  }

  std::string current_window_text() {
    return text.substr(this->window_start, this->window_end);
  }
};


double checker(std::string text, std::string pattern) {
    if (text == "" || pattern == "") {
        return 0.0;
    }
    if (pattern.length() > text.length()) {
        return 0.0;
    }

    // Create a Bloom filter and add all substrings of the text to it
    BloomFilter bloom(pattern.length());
    for (int i = 0; i < text.length() - pattern.length() + 1; i++) {
        auto t = text.substr(i, pattern.length());
        bloom.add(t);
    }

    RollingHash text_rolling(text, pattern.length());
    RollingHash pattern_rolling(pattern, pattern.length());

    int matchCount = 0;
    int totalCount = text.length() - pattern.length() + 1;

    for (int i = 0; i < totalCount; i++) {
        // First check the Bloom filter
        if (bloom.possiblyContains(pattern)) {
            // If the pattern could be in the text, do the Rabin-Karp check
            if (text_rolling.hash == pattern_rolling.hash) {
                matchCount++;
            }
        }
        text_rolling.next_window();
    }

    // Calculate the percentage similarity
    double similarity = (double)matchCount / totalCount * 100;
    return similarity;
}
double plagiarismRate(std::string text, std::string pattern) {
    if (text == "" || pattern == "") {
        return 0.0;
    }
    if (pattern.length() > text.length()) {
        return 0.0;
    }

    // Create a Bloom filter and add all substrings of the text to it
    BloomFilter bloom(pattern.length());
    for (int i = 0; i < text.length() - pattern.length() + 1; i++) {
        auto t = text.substr(i, pattern.length());
        bloom.add(t);
    }

    RollingHash text_rolling(text, pattern.length());
    RollingHash pattern_rolling(pattern, pattern.length());

    int matchCount = 0;
    int totalCount = pattern.length() - pattern.length() + 1;

    for (int i = 0; i < totalCount; i++) {
        // First check the Bloom filter
        if (bloom.possiblyContains(pattern)) {
            // If the pattern could be in the text, do the Rabin-Karp check
            if (text_rolling.hash == pattern_rolling.hash) {
                matchCount++;
            }
        }
        text_rolling.next_window();
    }

    // Calculate the plagiarism rate
    double plagiarism = (double)matchCount / totalCount * 100;
    return plagiarism;
}




struct AllowOriginMiddleware {
  struct context {};

  void before_handle(crow::request &req, crow::response &res, context &ctx) {
    res.set_header("Access-Control-Allow-Origin", "*");
    res.set_header("Access-Control-Allow-Methods", "POST");
    res.set_header("Access-Control-Allow-Headers", "Content-Type");
  }
};

int main() {
  crow::SimpleApp app;
  CROW_ROUTE(app, "/").methods("POST"_method)([&](auto req) {
    std::cout << "d1: " << std::endl;

    auto jsonBody = crow::json::load(req.body);
    if (!jsonBody) {
      return crow::response(400);
    }

    std::string d1 = jsonBody["d1"].s();
    std::string d2 = jsonBody["d2"].s();

    if (!d1.empty() && !d2.empty()) {
      auto result = plagiarismRate(d1, d2);
      std::cout << "s: " << result << std::endl;
      nlohmann::json j;
      j["p"] = result;
      crow::response res(j.dump());
      res.set_header("Access-Control-Allow-Origin", "*");
      res.set_header("Access-Control-Allow-Methods", "POST");
      res.set_header("Access-Control-Allow-Headers", "Content-Type");

      return res;
    } else {
      return crow::response(400);
    }
  });
  app.port(4437).multithreaded().run();
}