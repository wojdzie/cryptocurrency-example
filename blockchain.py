from hashlib import sha256


def update_hash(*args):
    hashing_text = ""
    h = sha256()
    for arg in args:
        hashing_text += str(arg)

    h.update(hashing_text.encode('utf-8'))

    return h.hexdigest()


class Block:
    def __init__(self, number=0, previous_hash="0" * 64, data=None, nonce=0):
        self.data = data
        self.number = number
        self.previous_hash = previous_hash
        self.nonce = nonce

    def hash(self):
        return update_hash(self.previous_hash, self.number, self.data, self.nonce)

    def __str__(self):
        return f"""
        Block#: {self.number} 
        Hash: {self.hash()}
        Previous: {self.previous_hash}
        Data: {self.data}
        Nonce: {self.nonce}
        """


class Blockchain:
    difficulty = 4

    def __init__(self):
        self.chain = []

    def add(self, block):
        self.chain.append(block)

    def remove(self, block):
        self.chain.remove(block)

    def mine(self, block):
        try:
            block.previous_hash = self.chain[-1].hash()
        except IndexError:
            pass

        while True:
            if block.hash()[:self.difficulty] == "0" * self.difficulty:
                self.add(block)
                break
            else:
                block.nonce += 1

    def is_valid(self):
        for i in range(1, len(self.chain)):
            _previous = self.chain[i].previous_hash
            _current = self.chain[i - 1].hash()
            if _previous != _current or _current[:self.difficulty] != "0" * self.difficulty:
                return False
        return True


def main():
    pass


if __name__ == '__main__':
    main()
