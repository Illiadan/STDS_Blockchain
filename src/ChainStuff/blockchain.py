from time import time

from block import Block


class Blockchain:
    def __init__(self):
        self.unconfirmedTransactions = []
        self.chain = []
        self.createGenesisBlock()

    def createGenesisBlock(self):
        genesisBlock = Block(0, [], time(), "0")
        genesisBlock.hash = genesisBlock.generateHash()
        self.chain.append(genesisBlock)

    @property
    def lastBlock(self):
        return self.chain[-1]

    difficulty = 2

    def proofOfWork(self, block):
        generatedHash = block.generateHash()

        while not generatedHash.startswith("0" * Blockchain.difficulty):
            block.nonce += 1
            generatedHash = block.generateHash()
        return generatedHash

    def addBlock(self, block, proof):
        prevHash = self.lastBlock.hash
        if prevHash != block.prevHash:
            return False
        if not self.isValidProof(block, proof):
            return False
        block.hash = proof
        self.chain.append(block)
        return True

    def isValidProof(self, block, blockHash):
        return (
            blockHash.startswith("0" * Blockchain.difficulty)
            and blockHash == block.generateHash()
        )

    def addNewTransaction(self, transaction):
        self.unconfirmedTransactions.append(transaction)

    def mine(self):
        if not self.unconfirmedTransactions:
            return False

        lastBlock = self.lastBlock
        newBlock = Block(
            lastBlock.index + 1,
            self.unconfirmedTransactions,
            time(),
            lastBlock.hash,
        )

        proof = self.proofOfWork(newBlock)
        self.addBlock(newBlock, proof)
        self.unconfirmedTransactions = []
        return newBlock.index
