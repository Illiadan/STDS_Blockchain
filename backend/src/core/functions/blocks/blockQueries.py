import core.models as cm


def getAllBlocks():
    blocks = cm.Block.objects.all()
    return blocks


def getAllBlocksCount():
    blocks = getAllBlocks()
    return len(blocks)


def getLastBlock():
    blocks = getAllBlocks()
    lastBlock = blocks.order_by("-id")[0]
    return lastBlock
