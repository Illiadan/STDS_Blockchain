from datetime import datetime, timedelta
import json

from django.core.serializers.json import DjangoJSONEncoder
from core.models import CalculationRange

# checks database for already calculated ranges and finds the next lower bound to calculate
def getNextLowerBound():
    sizeOfBounds = 10000
    newLowerBound = 0

    for range in CalculationRange.objects.order_by('lowerBound'):
        if range.lowerBound == newLowerBound:
            newLowerBound = newLowerBound + sizeOfBounds

    return newLowerBound


# checks database for unfinished ranges and deletes them, if its older than 5 min
def checkAndCleanupUnfinishedRanges():
    for range in CalculationRange.objects.filter(status__exact=CalculationRange.TODO):
        if range.timestamp + timedelta(minutes=5) < datetime.now():
            range.remove()


# generate packet to send to the clients as json
def combineBlockJsonWithBound(blockJson, lowerBound, lastBlock):
    entirePacket = {
            "block": json.loads(blockJson),
            "lowerBound": lowerBound,
            "lastBlock": lastBlock
            }

    return json.dumps(entirePacket, cls=DjangoJSONEncoder)
