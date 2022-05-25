from core.functions.blocks import blockQueries as fBQ
from core.functions.transactions import transactionQueries as fTQ


def transactionDatabaseUpdate(acceptedBlock):
    qsTransactionsIncluded = fTQ.getAllUnacceptedTransactions().filter(
        id__in=acceptedBlock.transactionsIncluded
    )
    dbBlock = fBQ.getAllBlocks().filter(id=acceptedBlock.id)[0]
    for transaction in qsTransactionsIncluded:
        transaction.blockContained = dbBlock
        transaction.save()
