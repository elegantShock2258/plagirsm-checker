#include <iostream>
#include <vector>
#include <bitset>

class BloomFilter {
    std::bitset<1000> bitset;
    int numHashes;

public:
    BloomFilter(int numHashes) : numHashes(numHashes) {}

    unsigned int hash1(std::string& input) {
        unsigned int value = 0;
        for (char c : input) {
            value = value * 101 + c;
        }
        return value;
    }

    unsigned int hash2(std::string& input) {
        unsigned int value = 0;
        for (char c : input) {
            value = value * 103 + c;
        }
        return value;
    }

    void add(std::string& input) {
        for (int n = 0; n < numHashes; n++) {
            unsigned int hashValue = (hash1(input) + n * hash2(input)) % bitset.size();
            bitset[hashValue] = 1;
        }
    }

    bool possiblyContains(std::string& input) {
        for (int n = 0; n < numHashes; n++) {
            unsigned int hashValue = (hash1(input) + n * hash2(input)) % bitset.size();
            if (bitset[hashValue] == 0) {
                return false;
            }
        }
        return true;
    }
};

int main() {
    BloomFilter filter(2);
    std::string str1 = "hello";
    std::string str2 = "world";
    filter.add(str1);
    filter.add(str2);

    std::cout << filter.possiblyContains(str1) << std::endl; // should print 1
    std::cout << filter.possiblyContains(str2) << std::endl; // should print 1

    return 0;
}