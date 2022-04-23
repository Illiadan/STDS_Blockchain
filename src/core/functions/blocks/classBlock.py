import json
import sys
from hashlib import sha256


class Block:
    def __init__(
        self,
        id,
        timestamp,
        transactionsIncluded,
        transactionsCount,
        transactionsValueTotal,
        miner,
        size,
        nonce,
        prevHash,
    ):
        self.id = id
        self.timestamp = timestamp
        self.transactionsIncluded = transactionsIncluded
        self.transactionsCount = transactionsCount
        self.transactionsValueTotal = transactionsValueTotal
        self.miner = miner
        self.size = size
        self.nonce = nonce
        self.prevHash = prevHash

    def generateHash(self):
        blockString = json.dumps(self.__dict__, sort_keys=True)
        return sha256(blockString.encode()).hexdigest()

    def determineSize(self):
        self.size = sys.getsizeof(self)
