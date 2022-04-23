import core.models as cm


def getAllTransactions():
    transactions = cm.Transaction.objects.all()
    return transactions


def getAllUnacceptedTransactions():
    unacceptedTransactions = cm.Transaction.objects.filter(blockContained=None)
    return unacceptedTransactions


def getAllUnacceptedTransactionsCount():
    unacceptedTransactions = getAllUnacceptedTransactions()
    return len(unacceptedTransactions)
