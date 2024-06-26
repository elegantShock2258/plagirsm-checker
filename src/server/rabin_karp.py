from pybloom_live import BloomFilter
class rolling_hash:
    def __init__(self, text, patternSize):
        self.text = text
        self.patternSize = patternSize
        self.base = 26
        self.window_start = 0
        self.window_end = 0
        self.mod = 11932
        self.hash = self.get_hash(text, patternSize)

    def get_hash(self, text, patternSize):
        hash_value = 0
        for i in range(0, patternSize):
            hash_value = (
                hash_value + (ord(self.text[i]) - 96)*(self.base**(patternSize - i - 1))) % self.mod

        self.window_start = 0
        self.window_end = patternSize

        return hash_value

    def next_window(self):
        if self.window_end <= len(self.text) - 1:
            self.hash -= (ord(self.text[self.window_start]) -
                          96)*self.base**(self.patternSize-1)

            self.hash *= self.base
            self.hash += ord(self.text[self.window_end]) - 96
            # print(  ord(self.text[self.window_end])- 96)
            self.hash %= self.mod
            self.window_start += 1
            self.window_end += 1
            return True
        return False

    def current_window_text(self):
        return self.text[self.window_start:self.window_end]



def checker(text, pattern):
    if text == "" or pattern == "":
        return None
    if len(pattern) > len(text):
        return None

    # Create a Bloom filter and add all substrings of the text to it
    bloom = BloomFilter(capacity=len(text))
    for i in range(len(text) - len(pattern) + 1):
        bloom.add(text[i:i+len(pattern)])

    text_rolling = rolling_hash(text.lower(), len(pattern))
    pattern_rolling = rolling_hash(pattern.lower(), len(pattern))

    for _ in range(len(text)-len(pattern)+1):
        # First check the Bloom filter
        if pattern in bloom:
            # If the pattern could be in the text, do the Rabin-Karp check
            if text_rolling.hash == pattern_rolling.hash:
                return "Found"
        text_rolling.next_window()
    return "Not Found"

if __name__ == "__main__":
    print(checker("asyush", "asyush"))
