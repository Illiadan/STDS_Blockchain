from hashlib import sha256
from random import randint

import core.models as cm
from core.functions.transactions import transactionQueries as fTQ


def transactionGeneration():
    unacceptedTransactions = fTQ.getAllUnacceptedTransactionsCount()
    if unacceptedTransactions < 20:
        createTransactions(50)


def createTransactions(amount):
    for x in range(amount):
        transactions = fTQ.getAllTransactions().values("id")
        transactionId = createUniqueId(transactions)
        blockContained = None
        sender, senderValue = createSenderAndValue()
        (
            recipient,
            recipientValue,
            fee,
            totalValue,
        ) = createRecipientAndValueAndFeeAndTotalValue(senderValue)
        transaction = cm.Transaction(
            id=transactionId,
            blockContained=blockContained,
            sender=sender,
            senderValue=senderValue,
            recipient=recipient,
            recipientValue=recipientValue,
            fee=fee,
            totalValue=totalValue,
        )
        transaction.save()


def createUniqueId(transactions):
    randomNumber = randint(1, 10**10)
    hash = sha256(str(randomNumber).encode()).hexdigest()
    while hash in transactions:
        randomNumber = randint(1, 10**10)
        hash = sha256(str(randomNumber).encode()).hexdigest()
    return hash


def createSenderAndValue():
    a = randint(1, 10)
    if a > 4:
        a = 1
    stringSender = ""
    stringValue = ""
    for x in range(a):
        randomNumber = randint(1, 10**10)
        hash = sha256(str(randomNumber).encode()).hexdigest()
        stringSender += hash
        rand = 168 / randint(1, 1000)
        stringValue += str("%.2f" % round(rand, 2))
        if x != a - 1:
            stringSender += ","
            stringValue += ","
    return stringSender, stringValue


def createRecipientAndValueAndFeeAndTotalValue(senderValue):
    a = randint(1, 10)
    if a > 6:
        a = 1
    stringRecipient = ""
    stringValue = ""
    listStringValues = senderValue.split(",")
    listFloatValues = list(map(float, listStringValues))
    sumValues = sum(listFloatValues)
    feeMult = randint(30, 2500) / 10000
    fee = max(float(str("%.2f" % round(sumValues * feeMult, 2))), 0.01)
    total = float(str("%.2f" % round(sumValues + fee, 2)))
    for x in range(a):
        randomNumber = randint(1, 10**10)
        hash = sha256(str(randomNumber).encode()).hexdigest()
        stringRecipient += hash
        val = sumValues / randint(2, 10)
        if x == a - 1:
            val = sumValues
        string = str("%.2f" % round(val, 2))
        stringValue += string
        sumValues -= float(string)
        if x != a - 1:
            stringRecipient += ","
            stringValue += ","
    return stringRecipient, stringValue, fee, total
