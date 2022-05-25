from django.shortcuts import render

from core.functions.blocks import blockGeneration as fBG
from core.functions.templateContext import blockUrl as fTCB
from core.functions.templateContext import coreUrl as fTCC
from core.functions.transactions import transactionGeneration as fTG
from core.models import Block


def coreUrl(request):
    if Block.objects.count() == 0:
        # generate genesis block mined by server
        fTG.transactionGeneration()
        fBG.blockGeneration()

        # generate next block mined by clients
        fTG.transactionGeneration()
        fBG.blockGeneration()

    context = fTCC.templateContextGeneration()
    return render(request, "coreLayout.html", context=context)


def blockUrl(request, value):
    context = fTCB.templateContextGeneration(value)
    return render(request, "blockLayout.html", context=context)

def miningUrl(request):
	return render(request, "miningTemplate.html")
