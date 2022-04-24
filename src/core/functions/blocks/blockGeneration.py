from datetime import datetime
from random import randint
from time import time

import core.models as cm
import requests
from core.functions.blocks import blockQueries as fBQ
from core.functions.blocks import classBlock as fCB
from core.functions.transactions import transactionDBUpdate as fTDBU
from core.functions.transactions import transactionQueries as fTQ
from django.utils.timezone import make_aware

# ---- MAIN FUNCTIONS ----


def addBlockToDatabase(block):
    timeString = formatTimestampToAwareDatetimeString(block.timestamp)
    transactionsIncluded = formatTransactionsIncludedToString(
        block.transactionsIncluded
    )
    dbBlock = cm.Block(
        id=block.id,
        timestamp=timeString,
        transactionsIncluded=transactionsIncluded,
        transactionsCount=block.transactionsCount,
        transactionsValueTotal=block.transactionsValueTotal,
        miner=block.miner,
        size=block.size,
        nonce=block.nonce,
        currHash=block.hash,
        prevHash=block.prevHash,
    )
    dbBlock.save()


def blockGeneration():
    blockchainDifficulty = 4
    numberOfBlocks = fBQ.getAllBlocksCount()
    if numberOfBlocks == 0:
        genBlock = generateGenesisBlock()
        addBlockToDatabase(genBlock)
    else:
        block = generateNewBlock(blockchainDifficulty)
        if blockValidation(block, blockchainDifficulty):
            addBlockToDatabase(block)
            fTDBU.transactionDatabaseUpdate(block)


def generateGenesisBlock():
    hostIP = getHostExternalIP()
    block = fCB.Block(0, time(), [], 0, 0.0, hostIP, 0, 0, "0")
    block.determineSize()
    block.hash = block.generateHash()
    return block


def generateNewBlock(difficulty):
    transactions, transactionsValue = getMostDesireableTransactions()
    if not transactions:
        return False

    minerIP = getHostExternalIP()
    lastBlock = fBQ.getLastBlock()
    newBlock = fCB.Block(
        lastBlock.id + 1,
        time(),
        transactions,
        len(transactions),
        transactionsValue,
        minerIP,
        0,
        0,
        lastBlock.currHash,
    )
    newBlock.determineSize()
    newBlock.hash = findNewHash(newBlock, difficulty)
    return newBlock


# ---- HELPER FUNCTIONS ----


def blockValidation(block, difficulty):
    lastBlock = fBQ.getLastBlock()
    testBlock = fCB.Block(
        block.id,
        block.timestamp,
        block.transactionsIncluded,
        block.transactionsCount,
        block.transactionsValueTotal,
        block.miner,
        block.size,
        block.nonce,
        block.prevHash,
    )
    if (
        lastBlock.currHash != block.prevHash
        or not block.hash.startswith("0" * difficulty)
        or testBlock.generateHash() != block.hash
    ):
        return False
    return True


def findNewHash(block: fCB.Block, difficulty):
    generatedHash = block.generateHash()

    while not generatedHash.startswith("0" * difficulty):
        block.nonce += 1
        block.determineSize()
        generatedHash = block.generateHash()

    return generatedHash


def formatTimestampToAwareDatetimeString(timestamp):
    datetimeObject = make_aware(datetime.utcfromtimestamp(timestamp))
    string = datetimeObject.strftime("%Y-%m-%d %H:%M:%S.%f")
    return string


def formatTransactionsIncludedToString(transactions):
    string = ""
    for idx in range(len(transactions)):
        string += transactions[idx]
        if idx != len(transactions) - 1:
            string += ","
    return string


def getHostExternalIP():
    ip = requests.get("https://api.ipify.org/").text
    return ip


def getMostDesireableTransactions():
    unacceptedTransactionPool = fTQ.getAllUnacceptedTransactions()
    transactionsUsedCount = simulateNumberOfIncludedTransactions(
        unacceptedTransactionPool
    )
    transactionsUsed, transactionsValue = getTransactionsUsedAndValue(
        unacceptedTransactionPool, transactionsUsedCount
    )
    return transactionsUsed, transactionsValue


def getTransactionsUsedAndValue(pool, quantity):
    poolSortedByFee = pool.order_by("-fee")
    transactionsUsed = []
    transactionsValue = 0
    for transaction in poolSortedByFee[:quantity]:
        transactionsUsed.append(transaction.id)
        transactionsValue += float(transaction.totalValue)
    return transactionsUsed, transactionsValue


def simulateNumberOfIncludedTransactions(unacceptedTransactions):
    capPerBlock = 40
    minPerBlock = 10
    currCap = min(capPerBlock, len(unacceptedTransactions))
    randomNumber = randint(minPerBlock, currCap)
    return randomNumber
