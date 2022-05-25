from datetime import datetime
import json
from random import randint
from time import time
from core.functions.transactions.transactionGeneration import transactionGeneration
import redis

import core.models as cm
import requests
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from core.functions.blocks import blockQueries as fBQ
from core.functions.blocks import classBlock as fCB
from core.functions.transactions import transactionQueries as fTQ
from django.utils.timezone import make_aware

from projectControl.settings import REDIS_HOST, REDIS_PORT

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
    blockchainDifficulty = 5
    numberOfBlocks = fBQ.getAllBlocksCount()
    if numberOfBlocks == 0:
        genBlock = generateGenesisBlock()
        addBlockToDatabase(genBlock)
    else:
        generateNewBlock(blockchainDifficulty)


def generateGenesisBlock():
    hostIP = getHostExternalIP()
    block = fCB.PreBlock(0, time(), [], 0, 0.0, 0, 0, "0", 0, miner=hostIP)
    block.determineSize()
    block.hash = block.generateHash()
    return block


def generateNewBlock(difficulty):
    transactions, transactionsValue = getMostDesireableTransactions()
    if not transactions:
        return False

    lastBlock = fBQ.getLastBlock()
    newBlock = fCB.PreBlock(
        lastBlock.id + 1,
        time(),
        transactions,
        len(transactions),
        transactionsValue,
        0,
        0,
        lastBlock.currHash,
		difficulty
    )
    newBlock.determineSize()

    redis_instance = redis.StrictRedis(host=REDIS_HOST, port=REDIS_PORT, db=0)
    redis_instance.set("newBlock", json.dumps(newBlock, cls=fCB.EntireBlockEncoder))

    channel_layer = get_channel_layer()
    cm.CalculationRange.objects.all().delete()
    newRange = cm.CalculationRange(lowerBound=0)
    newRange.save()

    async_to_sync(channel_layer.group_send)(
		"mining",
		{
			"type": "broadcast",
            "text": newBlock.generateJsonStringForClients(newRange.lowerBound, { "id": lastBlock.id, "timestamp": lastBlock.timestamp, "miner": lastBlock.miner })
		},
	)

# ---- HELPER FUNCTIONS ----


def blockValidation(block, difficulty):
    lastBlock = fBQ.getLastBlock()
    testBlock = fCB.PreBlock(
        block.id,
        block.timestamp,
        block.transactionsIncluded,
        block.transactionsCount,
        block.transactionsValueTotal,
        block.size,
        block.nonce,
        block.prevHash,
		difficulty
    )

    if (
        lastBlock.currHash != block.prevHash
        or not block.hash.startswith("0" * difficulty)
        or testBlock.generateHash() != block.hash
    ):
        return False
    return True


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
    ip = requests.get("https://ip.mdosch.de/").text
    return ip


def getMostDesireableTransactions():
    if fTQ.getAllUnacceptedTransactionsCount() <= 10:
        transactionGeneration()
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
