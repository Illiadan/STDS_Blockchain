from django.shortcuts import render

from core.functions.blocks import blockGeneration as fBG
from core.functions.blocks import blockQueries as fBQ
from core.functions.transactions import transactionDBUpdate as fTDBU
from core.functions.transactions import transactionGeneration as fTG
from core.functions.transactions import transactionQueries as fTQ


def coreUrl(request):
    blockchainDifficulty = 4
    numberOfBlocks = fBQ.getAllBlocksCount()
    if numberOfBlocks == 0:
        genBlock = fBG.generateGenesisBlock()
        fBG.addBlockToDatabase(genBlock)
    else:
        block = fBG.generateNewBlock(blockchainDifficulty)
        if fBG.blockValidation(block, blockchainDifficulty):
            fBG.addBlockToDatabase(block)
            fTDBU.transactionDatabaseUpdate(block)
    unacceptedTransactions = fTQ.getAllUnacceptedTransactionsCount()
    if unacceptedTransactions < 20:
        fTG.generateTransactions(50)
    return render(request, "coreLayout.html")


def blockUrl(request, value):
    return render(request, "blockLayout.html")
