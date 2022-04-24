from django.shortcuts import render

from core.functions.blocks import blockGeneration as fBG
from core.functions.templateContext import blockUrl as fTCB
from core.functions.templateContext import coreUrl as fTCC
from core.functions.transactions import transactionGeneration as fTG


def coreUrl(request):
    fBG.blockGeneration()
    fTG.transactionGeneration()
    context = fTCC.templateContextGeneration()
    return render(request, "coreLayout.html", context=context)


def blockUrl(request, value):
    context = fTCB.templateContextGeneration(value)
    return render(request, "blockLayout.html", context=context)
