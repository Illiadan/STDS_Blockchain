import json
from hashlib import sha256


class Block:
    def __init__(self, index, transactions, timestamp, prevHash, nonce=0):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.prevHash = prevHash
        self.nonce = nonce

    def generateHash(self):
        blockString = json.dumps(self.__dict__, sort_keys=True)
        return sha256(blockString.encode()).hexdigest()
