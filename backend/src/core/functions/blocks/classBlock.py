import json
import sys
from hashlib import sha256

from django.core.serializers.json import DjangoJSONEncoder

class PreBlock:
    def __init__(
        self,
        id,
        timestamp,
        transactionsIncluded,
        transactionsCount,
        transactionsValueTotal,
        size,
        nonce,
        prevHash,
		difficulty,
        miner=""
    ):
        self.id = id
        self.timestamp = timestamp
        self.transactionsIncluded = transactionsIncluded
        self.transactionsCount = transactionsCount
        self.transactionsValueTotal = transactionsValueTotal
        self.miner = miner
        self.size = size
        self.nonce = nonce
        self.hash = ""
        self.prevHash = prevHash
        self.difficulty = difficulty

    def generateHash(self):
        blockString = json.dumps(self, cls=BlockEncoder)
        return sha256(blockString.encode()).hexdigest()

    def determineSize(self):
        # calculate size in bytes
        size = sys.getsizeof(self.id)
        size += sys.getsizeof(self.timestamp)
        size += sys.getsizeof(self.transactionsCount)
        size += sys.getsizeof(self.transactionsValueTotal)
        # miner is omitted
        size += 101 # hash = string with 64 chars
        size += 101 # prevHash = string with 64 chars
        size += sys.getsizeof(self.difficulty)

        for tx in self.transactionsIncluded:
            size += sys.getsizeof(tx)

        self.size = size
        # self.size = sys.getsizeof(self)

    def generateJsonStringForClients(self, lowerBound, lastBlock):
        encodedPreBlock = json.dumps(self, cls=PreBlockEncoder)
        entirePacket = {
                "block": json.loads(encodedPreBlock),
                "lowerBound": lowerBound,
                "lastBlock": lastBlock
                }

        return json.dumps(entirePacket, cls=DjangoJSONEncoder)

	
# for sending the non finished block to our calculators
class PreBlockEncoder(DjangoJSONEncoder):
	def default(self, obj):
		if isinstance(obj, PreBlock):
			return {
					"id": obj.id,
					"timestamp": obj.timestamp,
					"transactionsIncluded": obj.transactionsIncluded,
					"transactionsCount": obj.transactionsCount,
					"size": obj.size,
					"prevHash": obj.prevHash,
					"difficulty": obj.difficulty
					}
		return DjangoJSONEncoder.default(self, obj)

# for generating the valid hash on serverside, to check if the found hash from our calculators is valid
class BlockEncoder(DjangoJSONEncoder):
	def default(self, obj):
		if isinstance(obj, PreBlock):
			return {
					"id": obj.id,
					"timestamp": obj.timestamp,
					"transactionsIncluded": obj.transactionsIncluded,
					"transactionsCount": obj.transactionsCount,
					"size": obj.size,
					"prevHash": obj.prevHash,
					"difficulty": obj.difficulty,
                    "nonce": obj.nonce
					}
		return DjangoJSONEncoder.default(self, obj)

class EntireBlockEncoder(DjangoJSONEncoder):
	def default(self, obj):
		if isinstance(obj, PreBlock):
			return {
					"id": obj.id,
					"timestamp": obj.timestamp,
					"transactionsIncluded": obj.transactionsIncluded,
					"transactionsCount": obj.transactionsCount,
                    "transactionsValueTotal": obj.transactionsValueTotal,
                    "miner": obj.miner,
					"size": obj.size,
					"prevHash": obj.prevHash,
					"difficulty": obj.difficulty,
                    "nonce": obj.nonce
					}
		return DjangoJSONEncoder.default(self, obj)
