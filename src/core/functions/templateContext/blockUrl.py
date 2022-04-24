from core.functions.blocks import blockQueries as fBQ
from core.functions.transactions import transactionQueries as fTQ


def templateContextGeneration(blockId):
    qsBlocks = fBQ.getAllBlocks().filter(id=blockId)
    block = qsBlocks[0]
    transactions = getTransactionsData(block)
    nextHash = getHashFromSuccessorBlock(block.id + 1)
    context = {
        "id": block.id,
        "transactions": transactions,
        "transactionsCount": block.transactionsCount,
        "miner": block.miner,
        "nonce": block.nonce,
        "acceptedAt": block.acceptedAt,
        "hash": block.currHash,
        "prevHash": block.prevHash,
        "nextHash": nextHash,
    }
    return context


def getHashFromSuccessorBlock(blockId):
    nextHash = ""
    qsBlocks = fBQ.getAllBlocks().filter(id=blockId)
    if len(qsBlocks) != 0:
        nextHash = qsBlocks[0].currHash
    return nextHash


def getTransactionsData(block):
    transactions = []
    transactionIds = block.transactionsIncluded.split(",")
    qsTransactions = fTQ.getAllTransactions().filter(id__in=transactionIds)
    for transaction in qsTransactions:
        sender = formatStringToStringList(transaction.sender)
        senderValue = formatStringToFloatList(transaction.senderValue)
        recipient = formatStringToStringList(transaction.recipient)
        recipientValue = formatStringToFloatList(transaction.recipientValue)
        transactionDict = {
            "id": transaction.id,
            "createdAt": transaction.createdAt,
            "sender": sender,
            "senderValue": senderValue,
            "recipient": recipient,
            "recipientValue": recipientValue,
            "fee": format(transaction.fee, ".3f"),
            "totalValue": format(transaction.totalValue, ".3f"),
        }
        transactions.append(transactionDict)
    return transactions


def formatStringToStringList(string):
    return string.split(",")


def formatStringToFloatList(string):
    return list(map(lambda x: format(float(x), ".3f"), string.split(",")))
